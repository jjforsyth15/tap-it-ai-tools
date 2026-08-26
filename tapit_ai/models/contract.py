from typing import Literal
from pydantic import BaseModel

class ContractIssue(BaseModel):
    severity: Literal["error", "warning"]
    backend_schema: str
    frontend_type: str
    field: str | None
    problem: str
    suggested_fix: str
    
class ContractReview(BaseModel):
    status: Literal["passed", "issues_found"]
    issues: list[ContractIssue]

class ContractFix(BaseModel):
    fixed_code: str