import json
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class BaseCheckpointer(ABC):
    """Abstract Base Class for state graph checkpointing."""

    @abstractmethod
    async def save(
        self, checkpoint_id: str, state: dict[str, Any], current_node: str
    ) -> None:
        """Saves the current state and node pointer."""
        pass

    @abstractmethod
    async def load(self, checkpoint_id: str) -> tuple[dict[str, Any], str] | None:
        """Loads the saved state and node pointer, or returns None."""
        pass


class MemoryCheckpointer(BaseCheckpointer):
    """In-memory state checkpointer for development and transient execution."""

    def __init__(self):
        self.storage: dict[str, tuple[dict[str, Any], str]] = {}

    async def save(
        self, checkpoint_id: str, state: dict[str, Any], current_node: str
    ) -> None:
        self.storage[checkpoint_id] = (dict(state), current_node)

    async def load(self, checkpoint_id: str) -> tuple[dict[str, Any], str] | None:
        if checkpoint_id in self.storage:
            state, current_node = self.storage[checkpoint_id]
            return dict(state), current_node
        return None


class FileCheckpointer(BaseCheckpointer):
    """Disk-based file checkpointer for persistence and resilience across execution restarts."""

    def __init__(self, directory: str = ".checkpoints"):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def _get_path(self, checkpoint_id: str) -> str:
        return os.path.join(self.directory, f"{checkpoint_id}.json")

    async def save(
        self, checkpoint_id: str, state: dict[str, Any], current_node: str
    ) -> None:
        path = self._get_path(checkpoint_id)
        data = {"state": state, "current_node": current_node}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def load(self, checkpoint_id: str) -> tuple[dict[str, Any], str] | None:
        path = self._get_path(checkpoint_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                return data["state"], data["current_node"]
        except Exception as e:
            logger.warning(f"Failed to load checkpoint file {path}: {str(e)}")
            return None


class StateGraph:
    """A lightweight, robust, and inspectable graph-based state machine orchestrator.

    Replicates LangGraph-like state graph routing, allowing deterministic state updates,
    node executions, and conditional transitions between states.
    """

    def __init__(self, checkpointer: BaseCheckpointer | None = None):
        self.nodes: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self.edges: dict[str, str] = {}
        self.conditional_edges: dict[str, Callable[[dict[str, Any]], str]] = {}
        self.checkpointer = checkpointer

    def add_node(self, name: str, action: Callable[[dict[str, Any]], Any]) -> None:
        """Registers a node function to the state graph."""
        self.nodes[name] = action

    def add_edge(self, source: str, target: str) -> None:
        """Registers a deterministic transition from source node to target node."""
        self.edges[source] = target

    def add_conditional_edge(
        self, source: str, router: Callable[[dict[str, Any]], str]
    ) -> None:
        """Registers a conditional transition routing function for the source node."""
        self.conditional_edges[source] = router

    async def _load_checkpoint(
        self, checkpoint_id: str | None, state: dict[str, Any], current_node: str
    ) -> tuple[dict[str, Any], str]:
        """Loads and returns state/node from checkpointer if available."""
        if self.checkpointer and checkpoint_id:
            checkpoint = await self.checkpointer.load(checkpoint_id)
            if checkpoint:
                logger.info(
                    f"StateGraph: Resuming execution from checkpoint '{checkpoint_id}' at node '{checkpoint[1]}'"
                )
                return checkpoint
        return state, current_node

    async def _execute_node(
        self, current_node: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Executes a registered graph node function dynamically."""
        if current_node not in self.nodes:
            raise ValueError(
                f"Node '{current_node}' is not registered in the StateGraph."
            )

        node_func = self.nodes[current_node]
        import inspect

        if inspect.iscoroutinefunction(node_func):
            return await node_func(state)

        state_update = node_func(state)
        if inspect.iscoroutine(state_update):
            return await state_update
        return state_update

    async def _determine_next_node(
        self, current_node: str, state: dict[str, Any]
    ) -> str:
        """Determines the next node path via static or conditional routing."""
        import inspect

        if current_node in self.conditional_edges:
            router = self.conditional_edges[current_node]
            if inspect.iscoroutinefunction(router):
                next_node = await router(state)
            else:
                next_node = router(state)
                if inspect.iscoroutine(next_node):
                    next_node = await next_node
            logger.info(
                f"StateGraph: Conditional routing from '{current_node}' to '{next_node}'"
            )
            return next_node

        if current_node in self.edges:
            next_node = self.edges[current_node]
            logger.info(
                f"StateGraph: Direct transition from '{current_node}' to '{next_node}'"
            )
            return next_node

        return "END"

    async def run(
        self,
        initial_state: dict[str, Any],
        entry_point: str,
        checkpoint_id: str | None = None,
    ) -> dict[str, Any]:
        """Runs the state machine, tracing state transitions step-by-step."""
        state = dict(initial_state)
        current_node = entry_point

        # Restore from checkpoint if available
        state, current_node = await self._load_checkpoint(
            checkpoint_id, state, current_node
        )

        while current_node and current_node != "END":
            logger.info(f"StateGraph: Executing node '{current_node}'")

            # Execute node to update state
            state_update = await self._execute_node(current_node, state)
            if state_update:
                state.update(state_update)

            # Determine next node via conditional or static edges
            next_node = await self._determine_next_node(current_node, state)

            # Save checkpoint before moving to the next node
            if self.checkpointer and checkpoint_id:
                await self.checkpointer.save(checkpoint_id, state, next_node)

            current_node = next_node

        logger.info("StateGraph: Execution completed.")
        return state
