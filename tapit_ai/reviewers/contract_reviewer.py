from openai import OpenAI
from pathlib import Path
from tapit_ai.models.contract import ContractReview


def review_contract(backend_file: Path, frontend_file: Path) -> ContractReview:
    client = OpenAI()
    backend_code = backend_file.read_text(encoding="utf-8")
    frontend_code = frontend_file.read_text(encoding="utf-8")
    
    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions="""
        You are an AI contract reviewer for TapIt.

Compare FastAPI/Pydantic backend schemas against corresponding
TypeScript frontend types.

Compatibility rules:
- Python str -> TypeScript string
- Python int -> TypeScript number
- Python float -> TypeScript number
- Python bool -> TypeScript boolean
- Python UUID -> TypeScript string
- Python datetime -> TypeScript string
- Python X | None -> TypeScript X | null
- Python enums may be represented as TypeScript strings.

Check for:
- missing fields
- extra fields
- incorrect field types
- incorrect nullability
- incorrect request/response object mappings

Severity rules:
- Use "error" when the frontend may incorrectly handle data returned by the backend.
- Response nullability mismatches are errors.
- Missing response fields are errors.
- Incorrect response object mappings are errors.
- Use "warning" when a frontend request type is narrower than what the backend accepts,
  but valid frontend requests are still compatible.

Set status to "issues_found" if at least one issue exists.
Set status to "passed" only if no issues exist.

Only report genuine API contract problems.
""",
        input=f"""
        BACKEND SCHEMAS:
        ----------------
        {backend_code}

        FRONTEND TYPES:
        ---------------
        {frontend_code}
        """,
            text_format=ContractReview
        )
    
    return response.output_parsed
