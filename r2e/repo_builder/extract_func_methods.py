import fire
import os
import re
from r2e.models import Repo
from r2e.utils.data import write_functions
from r2e.repo_builder.repo_args import RepoArgs
from r2e.paths import REPOS_DIR
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.repo_builder.fut_extractor.extract_repo_data import extract_repo_data

def remove_bom_from_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        with open(file_path, 'wb') as file:
            file.write(content)

def remove_bom_from_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.py'):  
                remove_bom_from_file(file_path)


def build_functions_and_methods(repo_args: RepoArgs):
    repo_dirs = list(REPOS_DIR.glob("dir*"))  # Get all directories starting with 'dir'
    for repo_dir in repo_dirs:
        extraction_dir = repo_dir / "extracted"
        extraction_dir.mkdir(parents=True, exist_ok=True)
        extraction_path = extraction_dir / f"{repo_dir.name}_extracted.json"
        
        if extraction_path.exists():
            if repo_args.overwrite_extracted:
                print(f"Overwriting existing functions and methods for {repo_dir.name}. Interrupt to cancel!")
            else:
                print(f"Extracted file for {repo_dir.name} already exists. Use --overwrite_extracted to overwrite existing.")
                continue
        
        remove_bom_from_directory(str(repo_dir))  
        repos = [Repo.from_file_path(str(repo_dir))]

        functions = []
        methods = []

        outputs = run_tasks_in_parallel_iter(
            extract_repo_data,
            repos,
            num_workers=repo_args.extraction_multiprocess,
            use_progress_bar=True,
            progress_bar_desc=f"Extracting from {repo_dir.name}..",
        )
        

    for output in outputs:
        if output.is_success():
            new_functions, new_methods = output.result  # type: ignore
            functions.extend(new_functions)
            methods.extend(new_methods)
        else:
            print(f"Error extracting repo data: {output.exception_tb}")

    print(f"Extracted {len(functions)} functions and {len(methods)} methods")

    write_functions(functions + methods, extraction_path)


if __name__ == "__main__":
    repo_args = fire.Fire(RepoArgs)
    build_functions_and_methods(repo_args)
