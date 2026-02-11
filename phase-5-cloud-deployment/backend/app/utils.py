"""
Utility Functions for Phase V Backend

Provides common utility functions used across the application.
"""

import re
from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta
import hashlib
import json


class StringUtils:
    """String manipulation utilities."""

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert text to URL-friendly slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        # Convert to lowercase
        text = text.lower()

        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)

        # Remove non-alphanumeric characters (except hyphens)
        text = re.sub(r'[^a-z0-9-]', '', text)

        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        return text

    @staticmethod
    def truncate(text: str, length: int, suffix: str = "...") -> str:
        """
        Truncate text to specified length.

        Args:
            text: Text to truncate
            length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= length:
            return text

        return text[:length - len(suffix)] + suffix

    @staticmethod
    def camel_to_snake(text: str) -> str:
        """
        Convert camelCase to snake_case.

        Args:
            text: Text in camelCase

        Returns:
            Text in snake_case
        """
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()

    @staticmethod
    def snake_to_camel(text: str) -> str:
        """
        Convert snake_case to camelCase.

        Args:
            text: Text in snake_case

        Returns:
            Text in camelCase
        """
        components = text.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])


class DateUtils:
    """Date and time utilities."""

    @staticmethod
    def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format datetime to string.

        Args:
            dt: Datetime object
            format: Format string

        Returns:
            Formatted datetime string
        """
        return dt.strftime(format)

    @staticmethod
    def parse_datetime(date_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        Parse datetime from string.

        Args:
            date_string: Date string
            format: Format string

        Returns:
            Datetime object
        """
        return datetime.strptime(date_string, format)

    @staticmethod
    def get_start_of_day(dt: datetime) -> datetime:
        """
        Get start of day (00:00:00).

        Args:
            dt: Datetime object

        Returns:
            Datetime at start of day
        """
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_end_of_day(dt: datetime) -> datetime:
        """
        Get end of day (23:59:59).

        Args:
            dt: Datetime object

        Returns:
            Datetime at end of day
        """
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def get_date_range(start: datetime, end: datetime) -> List[datetime]:
        """
        Get list of dates in range.

        Args:
            start: Start date
            end: End date

        Returns:
            List of dates
        """
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)
        return dates

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        Check if date is weekend.

        Args:
            dt: Datetime object

        Returns:
            True if weekend, False otherwise
        """
        return dt.weekday() >= 5  # Saturday=5, Sunday=6

    @staticmethod
    def add_business_days(dt: datetime, days: int) -> datetime:
        """
        Add business days to date (excluding weekends).

        Args:
            dt: Starting date
            days: Number of business days to add

        Returns:
            New datetime
        """
        current = dt
        added = 0

        while added < days:
            current += timedelta(days=1)
            if not DateUtils.is_weekend(current):
                added += 1

        return current


class DictUtils:
    """Dictionary manipulation utilities."""

    @staticmethod
    def flatten(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Flatten nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DictUtils.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """
        Deep merge two dictionaries.

        Args:
            dict1: First dictionary
            dict2: Second dictionary

        Returns:
            Merged dictionary
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DictUtils.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def remove_none_values(d: Dict) -> Dict:
        """
        Remove None values from dictionary.

        Args:
            d: Dictionary

        Returns:
            Dictionary without None values
        """
        return {k: v for k, v in d.items() if v is not None}


class ListUtils:
    """List manipulation utilities."""

    @staticmethod
    def chunk(lst: List, size: int) -> List[List]:
        """
        Split list into chunks.

        Args:
            lst: List to chunk
            size: Chunk size

        Returns:
            List of chunks
        """
        return [lst[i:i + size] for i in range(0, len(lst), size)]

    @staticmethod
    def deduplicate(lst: List) -> List:
        """
        Remove duplicates while preserving order.

        Args:
            lst: List with duplicates

        Returns:
            List without duplicates
        """
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def flatten(lst: List[List]) -> List:
        """
        Flatten nested list.

        Args:
            lst: Nested list

        Returns:
            Flattened list
        """
        return [item for sublist in lst for item in sublist]


class HashUtils:
    """Hashing utilities."""

    @staticmethod
    def md5(text: str) -> str:
        """
        Generate MD5 hash.

        Args:
            text: Text to hash

        Returns:
            MD5 hash
        """
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        """
        Generate SHA-256 hash.

        Args:
            text: Text to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def hash_dict(d: Dict) -> str:
        """
        Generate hash of dictionary.

        Args:
            d: Dictionary to hash

        Returns:
            Hash string
        """
        json_str = json.dumps(d, sort_keys=True)
        return HashUtils.sha256(json_str)


class FileUtils:
    """File manipulation utilities."""

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension.

        Args:
            filename: Filename

        Returns:
            File extension (without dot)
        """
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    @staticmethod
    def get_file_size_mb(size_bytes: int) -> float:
        """
        Convert bytes to megabytes.

        Args:
            size_bytes: Size in bytes

        Returns:
            Size in megabytes
        """
        return round(size_bytes / (1024 * 1024), 2)

    @staticmethod
    def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Check if file type is allowed.

        Args:
            filename: Filename
            allowed_extensions: List of allowed extensions

        Returns:
            True if allowed, False otherwise
        """
        extension = FileUtils.get_file_extension(filename)
        return extension in [ext.lower() for ext in allowed_extensions]
