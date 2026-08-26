import difflib
import typer
from pathlib import Path
from tapit_ai.environment import require_env
from tapit_ai.reviewers.contract_reviewer import review_contract
from tapit_ai.reviewers.fixer import generate_fix
from tapit_ai.utils.discovery import discover_contract_pairs
from tapit_ai.testing.agent import run as run_journey_tests
from tapit_ai.testing.models import TestStatus

app = typer.Typer(
    help="TapIt AI Development Tools."
)

review_app = typer.Typer(
    help="Run AI-powered code reviews."
)

app.add_typer(review_app, name="review")

test_app = typer.Typer(
    help="Run TapIt user journey tests."
)

app.add_typer(test_app, name="test")


def _require_command_env(*names: str) -> dict[str, str]:
    try:
        return require_env(*names)
    except RuntimeError as error:
        typer.echo(f"Configuration error: {error}", err=True)
        raise typer.Exit(code=1) from None

@review_app.command("contracts")
def review_contracts(
    report: bool = typer.Option(
        False, "--report", help="Display the full AI review report for each contract pair."
    ), 
    file: str | None = typer.Option(
        None, "--file", help="Review a specific contract pair by filename, e.g. -- file beta"
    ),
    fix: bool = typer.Option(
        False, "--fix", help="Interactively generate and apply an AI fix for frontend types with issues."
    )
):
    _require_command_env(
        "TAP_IT_BACKEND_PATH",
        "TAP_IT_FRONTEND_PATH",
        "OPENAI_API_KEY",
    )

    from tapit_ai.config import BACKEND_SCHEMA_DIR, FRONTEND_TYPES_DIR

    typer.echo("Discovering TapIt contracts...")
    
    pairs = discover_contract_pairs(BACKEND_SCHEMA_DIR, FRONTEND_TYPES_DIR)
    
    if file:
        file_name = file.lower()
        
        if file_name.endswith(".py") or file_name.endswith(".ts"):
            file_name = Path(file_name).stem
            
        pairs = [
            (backend_file, frontend_file)
            for backend_file, frontend_file in pairs
            if backend_file.stem == file_name
        ]
        
    if not pairs:
        typer.echo(f"No contract pairs found for {file}.")
        raise typer.Exit(code=1)
    
    typer.echo(f"Found {len(pairs)} contract pair(s).\n")

    all_errors = []
    all_warnings = []

    for backend_file, frontend_file in pairs:
        typer.echo(f"Reviewing {backend_file.name} <-> {frontend_file.name}")

        review = review_contract(backend_file, frontend_file)

        errors = [issue for issue in review.issues if issue.severity == "error"]
        warnings = [issue for issue in review.issues if issue.severity == "warning"]

        all_errors.extend(errors)
        all_warnings.extend(warnings)

        typer.echo(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

        if report:
            typer.echo("Full report:")
            for issue in review.issues:
                typer.echo("\n---------------")
                typer.echo(f"Severity: {issue.severity}")
                typer.echo(f"Backend Schema: {issue.backend_schema}")
                typer.echo(f"Frontend Type: {issue.frontend_type}")
                typer.echo(f"Field: {issue.field}")
                typer.echo(f"Problem: {issue.problem}")
                typer.echo(f"Suggested Fix: {issue.suggested_fix}")

        if fix and review.issues:
            typer.echo(f"\nGenerating fix for {frontend_file.name}...")

            fixed_code = generate_fix(backend_file, frontend_file, review)

            if not fixed_code.strip():
                typer.echo("Fix generation returned empty content; skipping.")
            else:
                current_code = frontend_file.read_text(encoding="utf-8")

                diff = difflib.unified_diff(
                    current_code.splitlines(keepends=True),
                    fixed_code.splitlines(keepends=True),
                    fromfile=f"{frontend_file.name} (current)",
                    tofile=f"{frontend_file.name} (fixed)",
                )

                diff_text = "".join(diff)

                if not diff_text:
                    typer.echo("Generated fix is identical to the current file; skipping.")
                else:
                    typer.echo(diff_text)

                    if typer.confirm(f"Apply this fix to {frontend_file.name}?"):
                        frontend_file.write_text(fixed_code, encoding="utf-8")
                        typer.echo(f"Applied fix to {frontend_file.name}.")
                    else:
                        typer.echo("Fix not applied.")

    if all_errors:
        typer.echo("\nContract review failed: ")
        typer.echo(f"{len(all_errors)} error(s) found.")
        typer.echo(f"{len(all_warnings)} warning(s) found.")
        raise typer.Exit(code=1)

    elif all_warnings:
        typer.echo("\nContract review passed with warnings: ")
        typer.echo(f"{len(all_warnings)} warning(s) found.")

    else:
        typer.echo("\nContract review passed: No issues found.")


@test_app.command("journeys")
def test_journeys():
    """Run all TapIt user journey tests (Playwright browser automation)."""
    _require_command_env(
        "TAPIT_BASE_URL",
        "TAPIT_TEST_EMAIL",
        "TAPIT_TEST_PASSWORD",
    )

    results = run_journey_tests()

    failures = [r for r in results if r.status == TestStatus.FAILED]
    warnings = [r for r in results if r.status == TestStatus.WARNING]

    if failures:
        typer.echo(f"\n{len(failures)} of {len(results)} journey test(s) failed.")
        raise typer.Exit(code=1)

    if warnings:
        typer.echo(
            f"\nAll {len(results)} journey test(s) passed "
            f"({len(warnings)} with warning(s))."
        )
    else:
        typer.echo(f"\nAll {len(results)} journey test(s) passed.")


if __name__ == "__main__":
    app()
