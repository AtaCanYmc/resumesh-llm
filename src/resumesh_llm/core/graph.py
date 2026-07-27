import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class StateGraph:
    """A lightweight, robust, and inspectable graph-based state machine orchestrator.

    Replicates LangGraph-like state graph routing, allowing deterministic state updates,
    node executions, and conditional transitions between states.
    """

    def __init__(self):
        self.nodes: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self.edges: dict[str, str] = {}
        self.conditional_edges: dict[str, Callable[[dict[str, Any]], str]] = {}

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

    async def run(
        self, initial_state: dict[str, Any], entry_point: str
    ) -> dict[str, Any]:
        """Runs the state machine, tracing state transitions step-by-step."""
        state = dict(initial_state)
        current_node = entry_point

        while current_node and current_node != "END":
            logger.info(f"StateGraph: Executing node '{current_node}'")
            if current_node not in self.nodes:
                raise ValueError(
                    f"Node '{current_node}' is not registered in the StateGraph."
                )

            # Execute node to update state
            state_update = await self.nodes[current_node](state)
            if state_update:
                state.update(state_update)

            # Determine next node via conditional or static edges
            if current_node in self.conditional_edges:
                next_node = self.conditional_edges[current_node](state)
                logger.info(
                    f"StateGraph: Conditional routing from '{current_node}' to '{next_node}'"
                )
            elif current_node in self.edges:
                next_node = self.edges[current_node]
                logger.info(
                    f"StateGraph: Direct transition from '{current_node}' to '{next_node}'"
                )
            else:
                next_node = "END"

            current_node = next_node

        logger.info("StateGraph: Execution completed.")
        return state
