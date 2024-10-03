from pydantic import BaseModel, Field


class LLMArgs(BaseModel):
    model_name: str = Field(
        "gpt-4-turbo-2024-04-09",
        description="The model name to use for the language model",
    )
    local_model_path: str | None = Field(
        None,
        description="Local path to the model and tokenizer",
    )

    n: int = Field(
        1,
        description="The number of completions to generate",
    )
    top_p: float = Field(
        0.95,
        description="The nucleus sampling probability",
    )
    max_tokens: int = Field(
        1024,
        description="The maximum number of tokens to generate",
    )
    temperature: float = Field(
        0.2,
        description="The temperature for the LLM request",
    )
    presence_penalty: float = Field(
        0.0,
        description="The presence penalty for the LLM request",
    )
    frequency_penalty: float = Field(
        0.0,
        description="The frequency penalty for the LLM request",
    )
    stop: list[str] = Field(
        [],
        description="The stop sequence for the LLM request",
    )

    multiprocess: int = Field(
        1,
        description="The number of processes to use for multiprocessing",
    )

    openai_timeout: int = Field(
        60,
        description="The timeout for the OpenAI API request",
    )

    use_cache: bool = Field(
        True,
        description="Whether to use the cache",
    )
    cache_batch_size: int = Field(
        1,
        description="The batch size for the cache",
    )

    ## vllm
    tensor_parallel_size: int = Field(
        1,
        description="Tensor parallel size for the VLLM runner",
    )
    dtype: str = Field(
        "bfloat16",
        description="Data type for the VLLM runner",
    )
    vllm_max_model_len: int = Field(
        4096,
        description="The maximum model length for the VLLM runner",
    )
    enforce_eager: bool = Field(
        True,
        description="Whether to enforce eager execution for the VLLM runner",
    )
    enable_prefix_caching: bool = Field(
        False,
        description="Whether to enable prefix caching for the VLLM runner",
    )

    class Config:
        protected_namespaces = ()
