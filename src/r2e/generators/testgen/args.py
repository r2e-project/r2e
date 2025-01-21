from r2e.llms.llm_args import LLMArgs
from r2e.execution.args import ExecutionArgs
from pydantic import Field


class TestGenArgs(LLMArgs):
    context_type: str = Field(
        "sliced",
        description="The context type to use for the language model",
    )
    oversample_rounds: int = Field(
        1,
        description="The number of rounds to oversample",
    )
    max_context_size: int = Field(
        6000,
        description="The maximum context size",
    )

    in_file: str | None = Field(
        None,
        description="The input file for the test generator",
    )

    function: str | None = Field(
        None,
        description="A specific function to generate tests for",
    )

    exp_id: str = Field(
        "temp",
        description="Experiment ID used for prefixing the generated tests file.",
    )

    save_chat: bool = Field(
        False,
        description="Whether to save the chat messages",
    )


class GenExecArgs(TestGenArgs, ExecutionArgs):
    max_rounds: int = Field(
        3,
        description="The maximum number of rounds to run the genexec process",
    )
    min_cov: float = Field(
        0.8,
        description="The minimum branch coverage to consider a test valid",
    )
    min_valid: float = Field(
        0.8,
        description="The minimum percentage of valid problems to achieve in the dataset",
    )
