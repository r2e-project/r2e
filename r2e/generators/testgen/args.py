from r2e.llms.llm_args import LLMArgs
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

    in_file: str = Field(
        None,
        description="The input file for the test generator",
    )

    exp_id: str = Field(
        "temp",
        description="Experiment ID used for prefixing the generated tests file.",
    )
