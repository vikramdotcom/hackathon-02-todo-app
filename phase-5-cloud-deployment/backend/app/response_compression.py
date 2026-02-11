"""
Response Compression System

Compress HTTP responses for bandwidth optimization.
"""

import logging
import gzip
import zlib
from typing import Optional

logger = logging.getLogger(__name__)


class ResponseCompressor:
    """Compress HTTP responses."""

    def __init__(self, min_size: int = 1024):
        """Initialize response compressor."""
        self.min_size = min_size

    def compress_gzip(self, data: bytes) -> bytes:
        """Compress data using gzip."""
        if len(data) < self.min_size:
            return data

        compressed = gzip.compress(data)
        logger.debug(f"Compressed {len(data)} bytes to {len(compressed)} bytes (gzip)")
        return compressed

    def compress_deflate(self, data: bytes) -> bytes:
        """Compress data using deflate."""
        if len(data) < self.min_size:
            return data

        compressed = zlib.compress(data)
        logger.debug(f"Compressed {len(data)} bytes to {len(compressed)} bytes (deflate)")
        return compressed

    def decompress_gzip(self, data: bytes) -> bytes:
        """Decompress gzip data."""
        return gzip.decompress(data)

    def decompress_deflate(self, data: bytes) -> bytes:
        """Decompress deflate data."""
        return zlib.decompress(data)


response_compressor = ResponseCompressor()
