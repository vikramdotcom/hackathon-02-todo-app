"""
Unit Tests for Utility Functions

Tests all utility functions in app/utils.py
"""

import pytest
from datetime import datetime, timedelta
from app.utils import (
    StringUtils,
    DateUtils,
    DictUtils,
    ListUtils,
    HashUtils,
    FileUtils
)


class TestStringUtils:
    """Test StringUtils functions."""

    def test_slugify_basic(self):
        """Test basic slugification."""
        assert StringUtils.slugify("Hello World") == "hello-world"

    def test_slugify_special_chars(self):
        """Test slugification with special characters."""
        assert StringUtils.slugify("Hello, World!") == "hello-world"

    def test_slugify_multiple_spaces(self):
        """Test slugification with multiple spaces."""
        assert StringUtils.slugify("Hello   World") == "hello-world"

    def test_truncate_short_text(self):
        """Test truncating text shorter than limit."""
        text = "Short"
        assert StringUtils.truncate(text, 10) == "Short"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        text = "This is a very long text"
        assert StringUtils.truncate(text, 10) == "This is..."

    def test_camel_to_snake(self):
        """Test camelCase to snake_case conversion."""
        assert StringUtils.camel_to_snake("camelCase") == "camel_case"
        assert StringUtils.camel_to_snake("myVariableName") == "my_variable_name"

    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion."""
        assert StringUtils.snake_to_camel("snake_case") == "snakeCase"
        assert StringUtils.snake_to_camel("my_variable_name") == "myVariableName"


class TestDateUtils:
    """Test DateUtils functions."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2026, 2, 11, 15, 30, 45)
        formatted = DateUtils.format_datetime(dt)
        assert formatted == "2026-02-11 15:30:45"

    def test_parse_datetime(self):
        """Test datetime parsing."""
        date_string = "2026-02-11 15:30:45"
        dt = DateUtils.parse_datetime(date_string)
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 11

    def test_get_start_of_day(self):
        """Test getting start of day."""
        dt = datetime(2026, 2, 11, 15, 30, 45)
        start = DateUtils.get_start_of_day(dt)
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

    def test_get_end_of_day(self):
        """Test getting end of day."""
        dt = datetime(2026, 2, 11, 15, 30, 45)
        end = DateUtils.get_end_of_day(dt)
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59

    def test_is_weekend(self):
        """Test weekend detection."""
        # Saturday
        saturday = datetime(2026, 2, 14)
        assert DateUtils.is_weekend(saturday) is True

        # Monday
        monday = datetime(2026, 2, 9)
        assert DateUtils.is_weekend(monday) is False

    def test_add_business_days(self):
        """Test adding business days."""
        # Start on Monday
        monday = datetime(2026, 2, 9)
        # Add 5 business days should give next Monday
        result = DateUtils.add_business_days(monday, 5)
        assert result.weekday() == 0  # Monday


class TestDictUtils:
    """Test DictUtils functions."""

    def test_flatten_simple(self):
        """Test flattening simple nested dict."""
        d = {"a": {"b": 1, "c": 2}}
        flattened = DictUtils.flatten(d)
        assert flattened == {"a.b": 1, "a.c": 2}

    def test_flatten_deep(self):
        """Test flattening deeply nested dict."""
        d = {"a": {"b": {"c": 1}}}
        flattened = DictUtils.flatten(d)
        assert flattened == {"a.b.c": 1}

    def test_deep_merge(self):
        """Test deep merging dictionaries."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        merged = DictUtils.deep_merge(dict1, dict2)
        assert merged == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    def test_remove_none_values(self):
        """Test removing None values."""
        d = {"a": 1, "b": None, "c": 3}
        cleaned = DictUtils.remove_none_values(d)
        assert cleaned == {"a": 1, "c": 3}


class TestListUtils:
    """Test ListUtils functions."""

    def test_chunk(self):
        """Test chunking list."""
        lst = [1, 2, 3, 4, 5, 6, 7]
        chunks = ListUtils.chunk(lst, 3)
        assert chunks == [[1, 2, 3], [4, 5, 6], [7]]

    def test_deduplicate(self):
        """Test deduplicating list."""
        lst = [1, 2, 2, 3, 1, 4]
        deduped = ListUtils.deduplicate(lst)
        assert deduped == [1, 2, 3, 4]

    def test_flatten(self):
        """Test flattening nested list."""
        lst = [[1, 2], [3, 4], [5]]
        flattened = ListUtils.flatten(lst)
        assert flattened == [1, 2, 3, 4, 5]


class TestHashUtils:
    """Test HashUtils functions."""

    def test_md5(self):
        """Test MD5 hashing."""
        text = "hello"
        hash_value = HashUtils.md5(text)
        assert len(hash_value) == 32
        assert hash_value == "5d41402abc4b2a76b9719d911017c592"

    def test_sha256(self):
        """Test SHA-256 hashing."""
        text = "hello"
        hash_value = HashUtils.sha256(text)
        assert len(hash_value) == 64

    def test_hash_dict(self):
        """Test dictionary hashing."""
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}  # Different order
        # Should produce same hash (keys are sorted)
        assert HashUtils.hash_dict(d1) == HashUtils.hash_dict(d2)


class TestFileUtils:
    """Test FileUtils functions."""

    def test_get_file_extension(self):
        """Test getting file extension."""
        assert FileUtils.get_file_extension("file.txt") == "txt"
        assert FileUtils.get_file_extension("file.tar.gz") == "gz"
        assert FileUtils.get_file_extension("noextension") == ""

    def test_get_file_size_mb(self):
        """Test converting bytes to MB."""
        assert FileUtils.get_file_size_mb(1048576) == 1.0
        assert FileUtils.get_file_size_mb(2097152) == 2.0

    def test_is_allowed_file_type(self):
        """Test checking allowed file types."""
        allowed = ["jpg", "png", "gif"]
        assert FileUtils.is_allowed_file_type("image.jpg", allowed) is True
        assert FileUtils.is_allowed_file_type("image.JPG", allowed) is True
        assert FileUtils.is_allowed_file_type("file.pdf", allowed) is False
