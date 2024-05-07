from pydantic import BaseModel, Field


class RepoArgs(BaseModel):
    ## cloning args
    repo_url: str | None = Field(
        None,
        description="URL of the repository to build",
    )
    local_repo_path: str | None = Field(
        None,
        description="Path to the local repository",
    )
    repo_paths_file: str | None = Field(
        None,
        description="Path to a json file containing a list of local paths",
    )
    repo_urls_file: str | None = Field(
        None,
        description="Path to a json file containing a list of URLs",
    )
    cloning_multiprocess: int = Field(
        16,
        description="Number of processes to use for cloning the repositories",
    )

    ## pycg args
    run_pycg: bool = Field(
        False,
        description="Whether to run PyCG on the repositories",
    )
    pycg_timeout: int = Field(
        5,
        description="Timeout for PyCG in minutes",
    )
    pycg_multiprocess: int = Field(
        16,
        description="Number of processes to use for running PyCG",
    )

    ## install args
    install_batch_size: int = Field(
        10,
        description="Number of repositories to install in parallel",
    )

    ## extraction args
    exp_id: str = Field(
        "temp",
        description="Experiment ID used for prefixing the extracted functions and methods.",
    )
    overwrite_extracted: bool = Field(
        False,
        description="Whether to overwrite the extracted functions and methods",
    )
    extraction_multiprocess: int = Field(
        16,
        description="Number of processes to use for extracting functions and methods",
    )
