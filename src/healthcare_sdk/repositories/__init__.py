"""Repositories package exports."""

from .storage import HealthCareStorage
from .postgreSqlStorage import PostgreSqlStorage

__all__ = ["HealthCareStorage", "PostgreSqlStorage"]
