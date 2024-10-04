# fmt: off
import click
from r2e.repo_builder.setup_repos import SetupRepos
from r2e.repo_builder.extract_func_methods import build_functions_and_methods

from r2e.repo_builder.repo_args import RepoArgs
from r2e.generators.testgen import TestGenArgs, R2ETestGenerator

@click.group()
def r2e():
    """R2E CLI tool."""
    pass


@r2e.command()
@click.option('--repo_url', '-r', help="URL of the repository to build")
@click.option('--local_repo_path', '-l', help="Path to the local repository")
@click.option('--repo_paths_file', '-p', help="Path to a json file containing a list of local paths")
@click.option('--repo_urls_file', '-u', help="Path to a json file containing a list of URLs")
@click.option('--cloning_multiprocess', '-m', default=16, type=int, help="Number of processes to use for cloning the repositories")
@click.option('--run_pycg', is_flag=True, help="Whether to run PyCG on the repositories")
@click.option('--pycg_timeout', default=5, type=int, help="Timeout for PyCG in minutes")
@click.option('--pycg_multiprocess', default=16, type=int, help="Number of processes to use for running PyCG")
def setup(**kwargs):
    """Set up the environment and clone repositories."""
    SetupRepos.clone_and_setup_repos(RepoArgs(**kwargs))
    click.echo("Setup completed successfully.")


# TODO: r2e install/build command for docker building
# if local mode, then suggest user to install the repo in the r2e environment
# @r2e.command()
# def build():
#     """Build the Docker image."""
#     pass


@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for prefixing the extracted functions and methods")
@click.option('--overwrite_extracted', '-o', is_flag=True, help="Whether to overwrite the extracted functions and methods")
@click.option('--extraction_multiprocess', '-m', default=16, type=int, help="Number of processes to use for extracting functions and methods")
@click.option('--disable_dunder_methods', is_flag=True, default=False, help="Disable dunder method filter")
@click.option('--disable_no_docstring', is_flag=True, default=False, help="Disable functions w/o docstring filter")
@click.option('--disable_signature_filters', is_flag=True, default=False, help="Disable function signature filters (args, returns)")
@click.option('--disable_keyword_filters', is_flag=True, default=False, help="Disable keyword filters (docstring, body, name)")
@click.option('--disable_wrapper_filters', is_flag=True, default=False, help="Disable filters for wrappers (decorators, etc.)")
@click.option('--disable_lines_filter', is_flag=True, default=False, help="Disable lines filter")
@click.option('--disable_all_filters', is_flag=True, default=False, help="Disable all filters")
def extract(**kwargs):
    """Extract functions and methods from repositories."""
    repo_args = RepoArgs(**kwargs)
    build_functions_and_methods(repo_args)
    click.echo("Extraction completed successfully.")
    
    
def _default_in_file(ctx, param, value):
    if not value:
        exp_id = ctx.params.get('exp_id')
        default_file = f"{exp_id}_extracted.json"
        click.echo(f"Warning: --in_file not provided. Using `{default_file}` as per `exp_id`.")
        return default_file
    return value


@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for prefixing the generated tests file")
@click.option('--in_file', '-i', callback=_default_in_file, help="The input file for the test generator. Defaults to {exp_id}_extracted.json if not provided.")
@click.option('--context_type', default="sliced", help="The context type to use for the language model")
@click.option('--oversample_rounds', default=1, type=int, help="The number of rounds to oversample")
@click.option('--max_context_size', default=6000, type=int, help="The maximum context size")
# LLMArgs options
@click.option('--multiprocess', '-m', default=1, type=int, help="The number of processes to use for multiprocessing")
@click.option('--model_name', default="gpt-4-turbo-2024-04-09", help="The model name to use for the language model")
@click.option('--n', default=1, type=int, help="The number of completions to generate")
@click.option('--top_p', default=0.95, type=float, help="The nucleus sampling probability")
@click.option('--max_tokens', default=1024, type=int, help="The maximum number of tokens to generate")
@click.option('--temperature', default=0.2, type=float, help="The temperature for the LLM request")
@click.option('--presence_penalty', default=0.0, type=float, help="The presence penalty for the LLM request")
@click.option('--frequency_penalty', default=0.0, type=float, help="The frequency penalty for the LLM request")
@click.option('--stop', multiple=True, default=[], help="The stop sequence for the LLM request")
@click.option('--openai_timeout', default=60, type=int, help="The timeout for the OpenAI API request")
@click.option('--use_cache', is_flag=True, default=True, help="Whether to use the cache for LLM queries. Default is True.")
@click.option('--cache_batch_size', default=30, type=int, help="The batch size for cache writes.")
def generate(**kwargs):
    """Generate equivalence tests for the extracted functions."""
    test_gen_args = TestGenArgs(**kwargs)
    R2ETestGenerator.generate(test_gen_args)
    click.echo("Test generation completed successfully.")


if __name__ == '__main__':
    r2e()
