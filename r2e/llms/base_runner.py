import json
from abc import ABC, abstractmethod

from tqdm import tqdm

from r2e.llms.llm_args import LLMArgs
from r2e.llms.cache_object import Cache
from r2e.llms.language_model import LanguageModel
from r2e.multiprocess import run_tasks_in_parallel


class BaseRunner(ABC):
    def __init__(self, args: LLMArgs, model: LanguageModel):
        self.args = args
        self.model = model
        self.client_kwargs: dict[str, str] = {}

        if self.args.use_cache:
            self.cache = Cache()
        else:
            self.cache = None

    def save_cache(self):
        if self.cache is not None:
            self.cache.save_cache()

    @abstractmethod
    def config(self) -> dict:
        pass

    @abstractmethod
    def _run_single(self, payload) -> list[str]:
        return []

    @staticmethod
    def run_single(combined_args) -> list[str]:
        """
        Run the model for a single payload and return the output
        Static method to be used in multiprocessing
        Calls the _run_single method with the combined arguments
        """
        cache: Cache | None
        call_method: callable  # type: ignore
        payload, cache, args, config, call_method = combined_args

        if cache is not None:
            cache_result = cache.get_from_cache(json.dumps([payload, config]))
            if cache_result is not None:
                return cache_result

        result = call_method(payload)
        assert len(result) == args.n

        return result

    def run_batch(self, payloads: list) -> list[list[str]]:
        outputs = []
        config = self.config()
        arguments = [
            (
                payload,
                self.cache,  ## pass the cache as argument for cache check
                self.args,  ## pass the args as argument for cache check
                config,
                self._run_single,  ## pass the _run_single method as argument because of multiprocessing
            )
            for payload in payloads
        ]
        if self.args.multiprocess > 1:
            parallel_outputs = run_tasks_in_parallel(
                self.run_single,
                arguments,
                self.args.multiprocess,
                use_progress_bar=self.args.use_progress_bar,
            )
            for output in parallel_outputs:
                if output.is_success():
                    outputs.append(output.result)
                else:
                    print("Failed to run the model for some payload")
                    print(output.status)
                    print(output.exception_tb)
                    outputs.extend([""] * self.args.n)
        else:
            outputs = [self.run_single(argument) for argument in tqdm(arguments)]

        if self.cache is not None:
            for payload, output in zip(payloads, outputs):
                self.cache.add_to_cache(
                    json.dumps([payload, config]), output
                )  ## save the output to cache
            self.save_cache()

        return outputs

    def run_main(self, payloads: list) -> list[list[str]]:
        if self.cache is not None:
            outputs = []
            batch_size = self.args.cache_batch_size
            for i in range(0, len(payloads), batch_size):
                payload_batch = payloads[i : i + batch_size]
                outputs_batch = self.run_batch(payload_batch)
                outputs.extend(outputs_batch)
        else:
            outputs = self.run_batch(payloads)
        return outputs
