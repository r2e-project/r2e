import os
import git
import json
import shutil
from pathlib import Path

import fire

from r2e.paths import REPOS_DIR
from r2e.repo_builder.run_pycg import run_pycg
from r2e.repo_builder.repo_args import RepoArgs
from r2e.multiprocess import run_tasks_in_parallel_iter


class SetupRepos:

    @staticmethod
    def clone_and_setup_repos(repo_args: RepoArgs):
        REPOS_DIR.mkdir(parents=True, exist_ok=True)
        if repo_args.repo_url:
            SetupRepos.clone_repo_from_url(repo_args.repo_url)

        elif repo_args.local_repo_path:
            SetupRepos.copy_repo(repo_args.local_repo_path)

        elif repo_args.repo_paths_file:
            with open(repo_args.repo_paths_file) as f:
                repo_paths: list[str] = json.load(f)
                assert isinstance(
                    repo_paths, list
                ), f"Expected list, got {type(repo_paths)}"
                assert all(
                    isinstance(x, str) for x in repo_paths
                ), f"Expected list of strings, got {repo_paths}"
            SetupRepos.copy_repos(repo_paths, repo_args.cloning_multiprocess)

        elif repo_args.repo_urls_file:
            with open(repo_args.repo_urls_file) as f:
                repo_urls: list[str] = json.load(f)
                assert isinstance(
                    repo_urls, list
                ), f"Expected list, got {type(repo_urls)}"
                assert all(
                    isinstance(x, str) for x in repo_urls
                ), f"Expected list of strings, got {repo_urls}"
            SetupRepos.clone_repos_from_urls(repo_urls, repo_args.cloning_multiprocess)

        #run_pycg(repo_args)

    @staticmethod
    def clone_repo_from_url(repo_url: str):
        repo_username, repo_name = (
            repo_url.rstrip("/").removesuffix(".git").split("/")[-2:]
        )
        local_repo_clone_path = REPOS_DIR / f"{repo_username}___{repo_name}"

        if os.path.exists(local_repo_clone_path):
            print(
                f"Repository {repo_url} already exists at {local_repo_clone_path}... skipping"
            )
            return

        print(f"Cloning repository {repo_url} to {local_repo_clone_path}")
        git.Repo.clone_from(f"{repo_url}", local_repo_clone_path)

    @staticmethod
    def copy_repo(local_repo_path: str):
        # convert relative to absolute path
        local_repo_path = str(Path(local_repo_path).resolve())

        local_repo_name = local_repo_path.split("/")[-1]
        local_repo_clone_path = REPOS_DIR / f"LOCAL___{local_repo_name}"

        if os.path.exists(local_repo_clone_path):
            print(
                f"Repository {local_repo_path} already exists at {local_repo_clone_path}... skipping"
            )
            return

        print(f"Copying repository {local_repo_path} to {local_repo_clone_path}")

        shutil.copytree(local_repo_path, local_repo_clone_path)

    @staticmethod
    def clone_repos_from_urls(repo_urls: list[str], cloning_multiprocess: int):
        if cloning_multiprocess > 0:
            output = run_tasks_in_parallel_iter(
                SetupRepos.clone_repo_from_url,
                repo_urls,
                cloning_multiprocess,
            )
            for result in output:
                if not result.is_success():
                    print(result.exception_tb)
        else:
            for repo_url in repo_urls:
                SetupRepos.clone_repo_from_url(repo_url)

    @staticmethod
    def copy_repos(local_repo_paths: list[str], cloning_multiprocess: int):
        if cloning_multiprocess > 0:
            output = run_tasks_in_parallel_iter(
                SetupRepos.copy_repo,
                local_repo_paths,
                cloning_multiprocess,
            )
            for result in output:
                if not result.is_success():
                    print(result.exception_tb)
        else:
            for local_repo_path in local_repo_paths:
                SetupRepos.copy_repo(local_repo_path)


if __name__ == "__main__":
    repo_args = fire.Fire(RepoArgs)
    SetupRepos.clone_and_setup_repos(repo_args)
