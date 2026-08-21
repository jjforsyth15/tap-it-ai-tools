from enum import Enum
from pydantic import BaseModel

class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    

class TestResult(BaseModel):
    scenario: str
    status: TestStatus
    summary: str
    details: list[str] = []