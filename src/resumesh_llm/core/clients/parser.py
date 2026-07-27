import json
import re
from typing import Any

from pydantic import BaseModel


class OutputParser:
    """Utility class to clean, parse, and validate JSON outputs from LLMs using strict Pydantic schemas."""

    @staticmethod
    def parse_json(text: str) -> Any:
        """Cleans markdown JSON code blocks and parses raw JSON string."""
        cleaned = text.strip()
        # Strip markdown JSON wrapping if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n```$", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    @staticmethod
    def parse_and_validate(text: str, model_class: type[BaseModel]) -> Any:
        """Parses the text and performs strict validation against the provided Pydantic model."""
        data = OutputParser.parse_json(text)
        # Perform strict Pydantic V2 validation
        return model_class.model_validate(data, strict=True)
