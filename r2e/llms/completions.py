from r2e.llms.llm_args import LLMArgs
from r2e.llms.language_model import LanguageModelStyle, LanguageModelList


class LLMCompletions:

    @staticmethod
    def get_llm_completions(args: LLMArgs, payloads: list) -> list[list[str]]:
        model_name = args.model_name
        matched_lang_model = [
            model for model in LanguageModelList if model.model_name == model_name
        ]
        assert len(matched_lang_model) == 1
        model = matched_lang_model[0]

        if model.style == LanguageModelStyle.OpenAI:
            from r2e.llms.openai_runner import OpenAIRunner

            runner = OpenAIRunner(args, model)
            return runner.run_main(payloads)

        raise ValueError(f"Unsupported model style: {model.style}")

    # @staticmethod
    # def get_llm_completions_async(args: LLMArgs, payloads: list) -> None:
    #     model_name = args.model_name
    #     matched_lang_model = [
    #         model for model in LanguageModelList if model.model_name == model_name
    #     ]
    #     assert len(matched_lang_model) == 1
    #     model = matched_lang_model[0]

    #     assert model.style == LanguageModelStyle.OpenAI

    #     from openai import OpenAI

    #     client = OpenAI()

    #     client.files.create(file=open("mydata.jsonl", "rb"), purpose="batch completions")

    #     client.batches.create(
    #         input_file_id="file-abc123",
    #         endpoint="/v1/chat/completions",
    #         completion_window="24h",
    #     )
