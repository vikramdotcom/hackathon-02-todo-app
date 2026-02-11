"""
Data Export and Import Utilities

Provides utilities for exporting and importing data in various formats.
"""

import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """Export data to various formats."""

    @staticmethod
    def to_json(data: List[Dict[str, Any]], pretty: bool = True) -> str:
        """
        Export data to JSON.

        Args:
            data: List of dictionaries
            pretty: Pretty print JSON

        Returns:
            JSON string
        """
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def to_csv(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
        """
        Export data to CSV.

        Args:
            data: List of dictionaries
            columns: Column names (defaults to keys from first item)

        Returns:
            CSV string
        """
        if not data:
            return ""

        output = io.StringIO()

        # Get columns from first item if not provided
        if columns is None:
            columns = list(data[0].keys())

        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()

        for row in data:
            # Filter to only include specified columns
            filtered_row = {k: v for k, v in row.items() if k in columns}
            writer.writerow(filtered_row)

        return output.getvalue()

    @staticmethod
    def to_xml(data: List[Dict[str, Any]], root_tag: str = "items", item_tag: str = "item") -> str:
        """
        Export data to XML.

        Args:
            data: List of dictionaries
            root_tag: Root element tag
            item_tag: Item element tag

        Returns:
            XML string
        """
        lines = [f'<?xml version="1.0" encoding="UTF-8"?>', f'<{root_tag}>']

        for item in data:
            lines.append(f'  <{item_tag}>')
            for key, value in item.items():
                # Escape XML special characters
                value_str = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                lines.append(f'    <{key}>{value_str}</{key}>')
            lines.append(f'  </{item_tag}>')

        lines.append(f'</{root_tag}>')

        return '\n'.join(lines)

    @staticmethod
    def to_markdown(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
        """
        Export data to Markdown table.

        Args:
            data: List of dictionaries
            columns: Column names

        Returns:
            Markdown string
        """
        if not data:
            return ""

        if columns is None:
            columns = list(data[0].keys())

        # Header
        lines = [
            '| ' + ' | '.join(columns) + ' |',
            '| ' + ' | '.join(['---'] * len(columns)) + ' |'
        ]

        # Rows
        for row in data:
            values = [str(row.get(col, '')) for col in columns]
            lines.append('| ' + ' | '.join(values) + ' |')

        return '\n'.join(lines)


class DataImporter:
    """Import data from various formats."""

    @staticmethod
    def from_json(json_str: str) -> List[Dict[str, Any]]:
        """
        Import data from JSON.

        Args:
            json_str: JSON string

        Returns:
            List of dictionaries
        """
        data = json.loads(json_str)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            raise ValueError("JSON must be a list or object")

    @staticmethod
    def from_csv(csv_str: str) -> List[Dict[str, Any]]:
        """
        Import data from CSV.

        Args:
            csv_str: CSV string

        Returns:
            List of dictionaries
        """
        input_stream = io.StringIO(csv_str)
        reader = csv.DictReader(input_stream)

        return list(reader)

    @staticmethod
    def from_xml(xml_str: str) -> List[Dict[str, Any]]:
        """
        Import data from XML.

        Args:
            xml_str: XML string

        Returns:
            List of dictionaries
        """
        try:
            import xml.etree.ElementTree as ET

            root = ET.fromstring(xml_str)
            data = []

            for item in root:
                item_dict = {}
                for child in item:
                    item_dict[child.tag] = child.text
                data.append(item_dict)

            return data

        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            raise


class BulkExporter:
    """Export large datasets efficiently."""

    @staticmethod
    def export_in_batches(
        data: List[Dict[str, Any]],
        format: str = "json",
        batch_size: int = 1000
    ) -> List[str]:
        """
        Export data in batches.

        Args:
            data: List of dictionaries
            format: Export format (json, csv)
            batch_size: Items per batch

        Returns:
            List of export strings
        """
        batches = []

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]

            if format == "json":
                batches.append(DataExporter.to_json(batch))
            elif format == "csv":
                batches.append(DataExporter.to_csv(batch))
            else:
                raise ValueError(f"Unsupported format: {format}")

        return batches


class DataTransformer:
    """Transform data between formats."""

    @staticmethod
    def flatten_nested(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        Flatten nested dictionary.

        Args:
            data: Nested dictionary
            prefix: Key prefix

        Returns:
            Flattened dictionary
        """
        result = {}

        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                result.update(DataTransformer.flatten_nested(value, new_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(DataTransformer.flatten_nested(item, f"{new_key}[{i}]"))
                    else:
                        result[f"{new_key}[{i}]"] = item
            else:
                result[new_key] = value

        return result

    @staticmethod
    def normalize_dates(data: List[Dict[str, Any]], date_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize date fields to ISO format.

        Args:
            data: List of dictionaries
            date_fields: Fields containing dates

        Returns:
            Normalized data
        """
        normalized = []

        for item in data:
            normalized_item = item.copy()

            for field in date_fields:
                if field in normalized_item and normalized_item[field]:
                    value = normalized_item[field]

                    if isinstance(value, datetime):
                        normalized_item[field] = value.isoformat()
                    elif isinstance(value, str):
                        # Already a string, keep as is
                        pass

            normalized.append(normalized_item)

        return normalized

    @staticmethod
    def filter_fields(data: List[Dict[str, Any]], include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Filter fields in data.

        Args:
            data: List of dictionaries
            include: Fields to include
            exclude: Fields to exclude

        Returns:
            Filtered data
        """
        filtered = []

        for item in data:
            filtered_item = {}

            for key, value in item.items():
                # Check include list
                if include and key not in include:
                    continue

                # Check exclude list
                if exclude and key in exclude:
                    continue

                filtered_item[key] = value

            filtered.append(filtered_item)

        return filtered


# Example usage
def export_todos_to_csv(todos: List[Dict[str, Any]]) -> str:
    """Export todos to CSV."""
    columns = ["id", "title", "completed", "priority", "due_date", "created_at"]
    return DataExporter.to_csv(todos, columns=columns)


def export_todos_to_json(todos: List[Dict[str, Any]]) -> str:
    """Export todos to JSON."""
    return DataExporter.to_json(todos, pretty=True)


def import_todos_from_csv(csv_str: str) -> List[Dict[str, Any]]:
    """Import todos from CSV."""
    return DataImporter.from_csv(csv_str)
