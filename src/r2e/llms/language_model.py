from enum import Enum
from dataclasses import dataclass


class LanguageModelStyle(Enum):
    """
    Used for setting up the client for sending payloads to the language model.
    """

    OpenAI = "openai"
    Gemini = "gemini"
    Claude3 = "claude3"
    VLLM = "vllm"


@dataclass
class LanguageModel:
    model_name: str
    style: LanguageModelStyle
    context_length: int = -1


LanguageModelList: list[LanguageModel] = [
    # LanguageModel(
    #     model_name="gpt-3.5-turbo",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-3.5-turbo-0613",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-3.5-turbo-1106",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-3.5-turbo-0125",
        style=LanguageModelStyle.OpenAI,
    ),
    # LanguageModel(
    #     model_name="gpt-3.5-turbo-16k",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-3.5-turbo-16k-0125",
        style=LanguageModelStyle.OpenAI,
    ),
    # LanguageModel(
    #     model_name="gpt-4",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-4-0613",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-4-0314",
        style=LanguageModelStyle.OpenAI,
    ),
    # LanguageModel(
    #     model_name="gpt-4-32k",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-4-32k-0613",
        style=LanguageModelStyle.OpenAI,
    ),
    # LanguageModel(
    #     model_name="gpt-4-turbo-preview",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-4-1106-preview",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-4-0125-preview",
        style=LanguageModelStyle.OpenAI,
    ),
    # LanguageModel(
    #     model_name="gpt-4-turbo",
    #     style=LanguageModelStyle.OpenAI,
    # ),
    LanguageModel(
        model_name="gpt-4-turbo-2024-04-09",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-4o-mini",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="gpt-4o",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="o1-preview",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="o1-mini",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="o3-mini",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="o3",
        style=LanguageModelStyle.OpenAI,
    ),
    LanguageModel(
        model_name="o4-mini",
        style=LanguageModelStyle.OpenAI,
    ),
]
