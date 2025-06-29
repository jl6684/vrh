"""
Helper functions for VRH data export operations.

This module contains utility functions used by the export commands
to handle data processing, datetime conversion, and other common operations.
"""
import datetime


def make_naive(dt):
    """
    Convert timezone-aware datetime to timezone-naive datetime.
    Required because Excel doesn't support timezone-aware datetimes.
    """
    if isinstance(dt, datetime.datetime) and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def dict_make_naive(d):
    """Convert all datetime values in a dictionary to timezone-naive."""
    return {k: make_naive(v) for k, v in d.items()} 