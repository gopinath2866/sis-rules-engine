"""
Pydantic schemas for SIS API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    rule_id: str = Field(...)
    resource_id: str = Field(...)
    resource_type: str = Field(...)
    severity: Severity = Field(...)
    message: str = Field(...)
    location: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None

class FileError(BaseModel):
    file_path: str = Field(...)
    error: str = Field(...)

class Summary(BaseModel):
    total_resources: int = Field(...)
    total_violations: int = Field(...)
    violations_by_severity: Dict[str, int] = Field(...)
    rules_evaluated: List[str] = Field(...)

class ScanRequest(BaseModel):
    files: List[Dict[str, Any]] = Field(...)

class ScanResponse(BaseModel):
    findings: List[Finding] = Field(...)
    summary: Summary = Field(...)
    errors: List[FileError] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str = Field(...)
    version: str = Field(...)
    uptime: Optional[float] = None

class Rule(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    type: str = Field(...)
    severity: Severity = Field(...)
    pattern: Dict[str, Any] = Field(...)
