from r2e.llms.llm_args import LLMArgs
from pydantic import Field


class SpecGenArgs(LLMArgs):
    in_file: str | None = Field(
        None,
        description="The input file for the spec generator",
    )

    exp_id: str = Field(
        "temp",
        description="Experiment ID used for prefixing the generated file.",
    )
