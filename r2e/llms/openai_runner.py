import os
from time import sleep
from typing import Any

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion

from r2e.llms.llm_args import LLMArgs
from r2e.llms.base_runner import BaseRunner
from r2e.llms.language_model import LanguageModel, LanguageModelStyle


class OpenAIRunner(BaseRunner):
    client = OpenAI(
        api_key=os.getenv("OPENAI_KEY"),
    )

    def __init__(self, args: LLMArgs, model: LanguageModel):
        super().__init__(args, model)
        if model.style == LanguageModelStyle.OpenAIReasoning:
            self.client_kwargs: dict[str, Any] = {
                "model": args.model_name,
                "max_completion_tokens": args.max_tokens,
            }
        else:
            self.client_kwargs: dict[str, Any] = {
                "model": args.model_name,
                "max_tokens": args.max_tokens,
                "temperature": args.temperature,
                "top_p": args.top_p,
                "frequency_penalty": args.frequency_penalty,
                "presence_penalty": args.presence_penalty,
                "n": args.n,
                "timeout": args.openai_timeout,
            }

    def config(self):
        return self.client_kwargs

    def _run_single(self, payload: list[dict[str, str]]) -> list[str]:
        assert isinstance(payload, list)

        try:
            response: ChatCompletion = OpenAIRunner.client.chat.completions.create(
                messages=payload,  # type: ignore
                **self.client_kwargs,
            )
        except openai.BadRequestError as e:
            return [
                f"OpenAI BadRequestError: {e}"
                for _ in range(self.client_kwargs.get("n", 1))
            ]
        except (
            openai.APIError,
            openai.RateLimitError,
            openai.InternalServerError,
            openai.OpenAIError,
            openai.APIStatusError,
            openai.APITimeoutError,
            openai.InternalServerError,
            openai.APIConnectionError,
        ) as e:
            print("Exception: ", repr(e))
            print("Sleeping for 30 seconds...")
            print("Consider reducing the number of parallel processes.")
            sleep(30)
            return self._run_single(payload)
        except Exception as e:
            print(f"Failed to run the model for {payload}!")
            print("Exception: ", repr(e))
            raise e
        return [c.message.content for c in response.choices]  # type: ignore
