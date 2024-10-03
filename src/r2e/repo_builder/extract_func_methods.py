import fire

from r2e.models import Repo
from r2e.utils.data import write_functions
from r2e.repo_builder.repo_args import RepoArgs
from r2e.paths import REPOS_DIR, EXTRACTION_DIR
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.repo_builder.fut_extractor.extract_repo_data import extract_repo_data


def build_functions_and_methods(repo_args: RepoArgs):
    EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)
    extraction_path = EXTRACTION_DIR / f"{repo_args.exp_id}_extracted.json"
    if extraction_path.exists():
        if repo_args.overwrite_extracted:
            print("Overwriting existing functions and methods. Interrupt to cancel!")
        else:
            print(
                "Extracted file already exists. Use --overwrite_extracted to overwrite existing."
            )
            return

    repo_dirs = list(REPOS_DIR.glob("*"))
    repos = [(Repo.from_file_path(str(repo_dir)), repo_args) for repo_dir in repo_dirs]

    functions = []
    methods = []

    outputs = run_tasks_in_parallel_iter(
        extract_repo_data,
        repos,
        num_workers=repo_args.extraction_multiprocess,
        use_progress_bar=True,
        progress_bar_desc="Extracting..",
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
