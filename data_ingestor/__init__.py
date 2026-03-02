"""Data ingestion module."""

from .ingestor import ingest_files
from .models import DocumentInfo, IngestResult

__all__ = ["ingest_files", "DocumentInfo", "IngestResult"]
