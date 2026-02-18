"""Tests for metadata utility helpers: property serialization and date stamping."""

import datetime
from unittest.mock import patch

import pytest
from graphrag_toolkit.lexical_graph.indexing.utils.metadata_utils import (
    get_properties_str,
    last_accessed_date,
)


# --- get_properties_str: sorted key:value pairs joined by ';', falls back to default ---


@pytest.mark.parametrize("properties,default,expected", [
    ({"b": 2, "a": 1}, "x", "a:1;b:2"),
    ({"single": "v"}, "x", "single:v"),
    ({}, "default", "default"),
    (None, "default", "default"),
])
def test_get_properties_str(properties, default, expected):
    assert get_properties_str(properties, default) == expected


# --- last_accessed_date: returns today's date as YYYY-MM-DD in a dict ---


def test_last_accessed_date():
    """Mocks datetime.now to verify the output format."""
    fake_now = datetime.datetime(2025, 6, 15, 12, 0, 0)
    with patch("graphrag_toolkit.lexical_graph.indexing.utils.metadata_utils.datetime") as mock_dt:
        mock_dt.datetime.now.return_value = fake_now
        mock_dt.datetime.strftime = datetime.datetime.strftime
        result = last_accessed_date()
        assert result == {"last_accessed_date": "2025-06-15"}
