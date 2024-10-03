from pydantic import BaseModel, Field


class ExecutionArgs(BaseModel):
    testgen_exp_id: str = Field(
        "r2e_v1_generate",
        description="The experiment ID used for the test generation",
    )

    execution_multiprocess: int = Field(
        20,
        description="The number of processes to use for executing the functions and methods",
    )

    port: int = Field(3006, description="The port to use for the execution service")

    timeout_per_task: int = Field(
        180, description="The timeout for the execution service in seconds"
    )
