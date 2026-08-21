from pathlib import Path

def discover_contract_pairs(backend_dir: Path, frontend_dir: Path) -> list[tuple[Path, Path]]:
    backend_files = list(backend_dir.glob("*.py"))
    frontend_files = list(frontend_dir.glob("*.ts"))

    frontend_by_name = {file.stem: file for file in frontend_files}
    
    pairs = []
    
    for backend_file in backend_files:
        frontend_file = frontend_by_name.get(backend_file.stem)
        
        if frontend_file:
            pairs.append((backend_file, frontend_file))
            
    return pairs