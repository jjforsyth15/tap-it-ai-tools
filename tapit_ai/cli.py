import typer
from pathlib import Path
from tapit_ai.config import (BACKEND_SCHEMA_DIR, FRONTEND_TYPES_DIR )
from tapit_ai.reviewers.contract_reviewer import review_contract
from tapit_ai.utils.discovery import discover_contract_pairs

app = typer.Typer(
    help="TapIt AI Development Tools."
)

review_app = typer.Typer(
    help="Run AI-powered code reviews."
)

app.add_typer(review_app, name="review")

@review_app.command("contracts")
def review_contracts(
    report: bool = typer.Option(
        False, "--report", help="Display the full AI review report for each contract pair."
    ), 
    file: str | None = typer.Option(
        None, "--file", help="Review a specific contract pair by filename, e.g. -- file beta"
    )
):
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
                
                
if __name__ == "__main__":
    app()