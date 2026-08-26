from openai import OpenAI
from pathlib import Path
from tapit_ai.models.contract import ContractFix, ContractReview

client = OpenAI()

def generate_fix(backend_file: Path, frontend_file: Path, review: ContractReview) -> str:
    backend_code = backend_file.read_text(encoding="utf-8")
    frontend_code = frontend_file.read_text(encoding="utf-8")

    issues_text = "\n".join(
        f"- [{issue.severity}] field={issue.field}: {issue.problem} "
        f"(suggested fix: {issue.suggested_fix})"
        for issue in review.issues
    )

    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions="""
        You are an AI contract fixer for TapIt.

        You will be given a backend Pydantic schema (source of truth, do not
        change it) and the current frontend TypeScript type file that should
        match it, along with a list of contract issues found between them.

        Return the FULL corrected contents of the frontend TypeScript file,
        with all listed issues resolved so that it accurately matches the
        backend schema. Preserve existing formatting, naming conventions,
        unrelated types, comments, and imports in the file wherever they are
        not implicated by an issue. Do not include markdown code fences or
        any commentary -- return only the raw file contents.
        """,
        input=f"""
        BACKEND SCHEMA (source of truth):
        ----------------------------------
        {backend_code}

        CURRENT FRONTEND TYPE FILE:
        ----------------------------
        {frontend_code}

        ISSUES TO FIX:
        --------------
        {issues_text}
        """,
        text_format=ContractFix,
    )

    return response.output_parsed.fixed_code
