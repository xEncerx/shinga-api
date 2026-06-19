import json

import pytest

from src.domain.models.source import Source
from src.infrastructure.sources.source_headers_loader import SourceHeadersLoader


class TestSourceHeadersLoader:
    def test_load_returns_none_when_source_file_is_missing(self, tmp_path):
        loader = SourceHeadersLoader(tmp_path)

        assert loader.load(Source.REMANGA) is None

    def test_load_reads_headers_for_source(self, tmp_path):
        headers = {
            "Authorization": "Bearer secret",
            "X-Custom-Header": "value",
        }
        (tmp_path / "remanga.json").write_text(
            json.dumps(headers), encoding="utf-8"
        )
        loader = SourceHeadersLoader(tmp_path)

        assert loader.load(Source.REMANGA) == headers

    def test_load_rejects_non_string_header_values(self, tmp_path):
        (tmp_path / "remanga.json").write_text(
            json.dumps({"X-Retry": 3}), encoding="utf-8"
        )
        loader = SourceHeadersLoader(tmp_path)

        with pytest.raises(ValueError, match="must be strings"):
            loader.load(Source.REMANGA)
