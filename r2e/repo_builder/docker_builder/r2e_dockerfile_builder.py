import os
import subprocess

import fire

from r2e.paths import REPOS_DIR
from r2e.repo_builder.repo_args import RepoArgs


def generate_dockerfile(repo_args: RepoArgs):
    with open("r2e/repo_builder/docker_builder/r2e_base_dockerfile.txt", "r") as f:
        dockerfile = f.read()

    num_repos = len(os.listdir(REPOS_DIR))
    batch_size = repo_args.install_batch_size

    dockerfile += f"COPY . /repos\n\n"

    dockerfile += f"WORKDIR /install_code\n\n"

    dockerfile += f"RUN pip install -r requirements.txt\n\n"

    for i in range(0, num_repos, batch_size):
        dockerfile += (
            f"RUN python3 parallel_installer.py {i} {i+batch_size} {batch_size}\n\n"
        )

    DOCKERFILE_PATH = REPOS_DIR / "r2e_final_dockerfile.dockerfile"
    with open(DOCKERFILE_PATH, "w") as f:
        f.write(dockerfile)

    print("Dockerfile generated at: ", DOCKERFILE_PATH)


if __name__ == "__main__":
    repo_args = fire.Fire(RepoArgs)
    generate_dockerfile(repo_args)
