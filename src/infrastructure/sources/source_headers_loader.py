from json import JSONDecodeError, loads
from pathlib import Path

from src.domain.models.source import Source

__all__ = ["SourceHeadersLoader"]


class SourceHeadersLoader:
    """Loads optional per-source HTTP headers from JSON files."""

    def __init__(self, headers_dir: str | Path) -> None:
        self._headers_dir = Path(headers_dir)

    def load(self, source: Source) -> dict[str, str] | None:
        headers_path = self._headers_dir / f"{source.name.lower()}.json"

        if not headers_path.exists():
            return None

        try:
            data = loads(headers_path.read_text(encoding="utf-8"))
        except JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in source headers file: {headers_path}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                f"Source headers file must contain a JSON object: {headers_path}"
            )

        if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in data.items()
        ):
            raise ValueError(
                f"Source header names and values must be strings: {headers_path}"
            )

        return data
