from pydantic import BaseModel, Field


class ExecutionArgs(BaseModel):
    execution_multiprocess: int = Field(
        20,
        description="The number of processes to use for executing the functions and methods",
    )

    image: str = Field(
        "r2e:temp",
        description="The name of the docker image in which to run the tests",
    )

    port: int = Field(3006, description="The port to use for the execution service")

    timeout_per_task: int = Field(
        180, description="The timeout for the execution service in seconds"
    )

    batch_size: int = Field(
        100,
        description="The number of functions to run before writing the output to the file",
    )

    local: bool = Field(
        False,
        description="Whether to run the execution service locally",
    )

    function: str | None = Field(
        None,
        description="A specific function to generate tests for",
    )

    in_file: str = Field(
        None,
        description="The input file for the test execution",
    )

    exp_id: str = Field(
        "temp",
        description="The experiment ID used for the test execution",
    )
