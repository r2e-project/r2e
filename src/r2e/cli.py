# fmt: off
import click
from r2e.repo_builder.setup_repos import SetupRepos
from r2e.repo_builder.extract_func_methods import build_functions_and_methods
from r2e.repo_builder.repo_args import RepoArgs

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


if __name__ == '__main__':
    r2e()
