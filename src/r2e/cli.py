# fmt: off
import os
import click
import ast
import json
import textwrap
import subprocess

from r2e.repo_builder import RepoArgs, SetupRepos, build_functions_and_methods, generate_dockerfile
from r2e.generators.testgen import TestGenArgs, R2ETestGenerator, GenExecArgs, R2EGenExec
from r2e.execution.args import ExecutionArgs
from r2e.execution.execute import EquivalenceTestRunner
from r2e.evaluators.testgen import summarize

from r2e.utils.data import load_functions, load_functions_under_test
from r2e.models import *

from r2e.paths import REPOS_DIR, EXTRACTED_DATA_DIR, TESTGEN_DIR, EXECUTION_DIR

@click.group()
def r2e():
    """R2E CLI tool."""
    pass

def show_result_file(file_path):
    click.secho(f"\nResult: {file_path}", fg="green", bold=True)

################### r2e setup ###################

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
    show_result_file(REPOS_DIR)


################### r2e build ###################

# TODO: r2e install/build command for docker building
# if local mode, then suggest user to install the repo in the r2e environment
@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for identifying the Docker image")
@click.option('--local', is_flag=True, default=False, help="Whether to run the build locally. Default is building a Docker image.")
@click.option('--install-batch-size', '-k', default=10, type=int, help="Number of repositories to install in parallel in the Docker container.")
def build(**kwargs):
    """Build a Docker image for your experiment."""
    repo_count = len([d for d in os.listdir(REPOS_DIR) if os.path.isdir(os.path.join(REPOS_DIR, d))])
    if repo_count == 0:
        click.echo("No repositories found in the repos directory. Please run the setup command first.")
        return
    
    click.echo(f"Found {repo_count} repositories in the repos directory.")
    
    if kwargs['local']:
        click.echo("Running in local mode.")
        click.secho("WARNING: If using `local` mode, please install repositories in the below directory manually.", fg="yellow")
        click.echo(f"    Repos directory path: {REPOS_DIR}")
        click.echo("    Note: Ensure you're installing in the r2e virtual env.")

    else:
        click.echo("Running in Docker mode.")
        click.echo("Creating a dockerfile...")
        generate_dockerfile(RepoArgs(**kwargs))
    
        click.secho("WARNING: Building the image will take a while (recommended: Use tmux). Continue? [y/n]", fg="yellow")        
        if input().lower() != 'y':
            click.echo("Exiting...")
            return
        
        click.echo("\nBuilding the Docker image...")
        
        click.secho(f"WARNING: All {repo_count} repos will be installed in the container. Continue? [y/n]", fg="yellow")
        if input().lower() != 'y':
            click.echo("Exiting...")
            return
        
        exp_id = kwargs['exp_id']
        path_to_dockerfile = REPOS_DIR / "r2e_final_dockerfile.dockerfile"
        cmd = f"docker build -t r2e:{exp_id} -f {path_to_dockerfile} ."
        
        try:
            subprocess.run(cmd, shell=True, check=True, cwd=REPOS_DIR)
        except subprocess.CalledProcessError as e:
            click.secho(f"Error building the Docker image: {e}", fg="red")
            return
    
        click.secho("\nDocker image built successfully.", fg="green")


################### r2e extract ###################

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
    show_result_file(os.path.join(EXTRACTED_DATA_DIR, f"{repo_args.exp_id}_extracted.json"))


################### r2e generate ###################

def gen_options(f):
    options = [
        click.option('--context_type', default="sliced", help="The context type to use for the language model"),
        click.option('--oversample_rounds', default=1, type=int, help="The number of rounds to oversample"),
        click.option('--max_context_size', default=6000, type=int, help="The maximum context size"),
        click.option('--save_chat', is_flag=True, default=False, help="Whether to save the chat messages"),
    ]
    for opt in reversed(options):
        f = opt(f)
    return f

def llm_options(f):
    options = [
        click.option('--multiprocess', '-m', default=8, type=int, help="The number of processes to use for multiprocessing"),
        click.option('--model_name', default="gpt-4-turbo-2024-04-09", help="The model name to use for the language model"),
        click.option('--n', default=1, type=int, help="The number of completions to generate"),
        click.option('--top_p', default=0.95, type=float, help="The nucleus sampling probability"),
        click.option('--max_tokens', default=1024, type=int, help="The maximum number of tokens to generate"),
        click.option('--temperature', default=0.2, type=float, help="The temperature for the LLM request"),
        click.option('--presence_penalty', default=0.0, type=float, help="The presence penalty for the LLM request"),
        click.option('--frequency_penalty', default=0.0, type=float, help="The frequency penalty for the LLM request"),
        click.option('--stop', multiple=True, default=[], help="The stop sequence for the LLM request"),
        click.option('--openai_timeout', default=60, type=int, help="The timeout for the OpenAI API request"),
        click.option('--use_cache', is_flag=True, default=True, help="Whether to use the cache for LLM queries. Default is True."),
        click.option('--cache_batch_size', default=30, type=int, help="The batch size for cache writes.")
    ]
    for opt in reversed(options):
        f = opt(f)
    return f

def _default_in_file_gen(ctx, param, value):
    if not value:
        exp_id = ctx.params.get('exp_id')
        default_file = f"{exp_id}_extracted.json"
        click.echo(f"Warning: --in_file not provided. Using `{default_file}` as per `exp_id`.")
        return default_file
    return value


@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for prefixing the generated tests file")
@click.option('--function', '-f', default=None, help="Name of the function to show.")
@click.option('--in_file', '-i', callback=_default_in_file_gen, help="The input file for the test generator. Defaults to {exp_id}_extracted.json if not provided.")
@gen_options
@llm_options
def generate(**kwargs):
    """Generate equivalence tests for the extracted functions."""
    test_gen_args = TestGenArgs(**kwargs)
    R2ETestGenerator.generate(test_gen_args)
    click.echo("Test generation completed successfully.")
    show_result_file(os.path.join(TESTGEN_DIR, f"{test_gen_args.exp_id}_generate.json"))


################### r2e execute ###################

def exec_options(f):
    options = [
        click.option('--local', is_flag=True, default=False, help="Whether to run the execution service locally. Default is docker."),
        click.option('--image', default="r2e:temp", help="The name of the docker image in which to run the tests"),
        click.option('--execution-multiprocess', '-m', default=20, type=int, help="The number of processes to use for executing the functions and methods"),
        click.option('--port', default=3006, type=int, help="The port to use for the execution service. Default is 3006 for sequential execution. For parallel, port is randomly picked."),
        click.option('--timeout-per-task', default=180, type=int, help="The timeout for the execution service to complete one task in seconds"),
        click.option('--batch-size', default=100, type=int, help="The number of functions to run before writing the output to the file")
    ]
    for opt in reversed(options):
        f = opt(f)
    return f

def _default_in_file_exec(ctx, param, value):
    if not value:
        exp_id = ctx.params.get('exp_id')
        default_file = f"{exp_id}_generate.json"
        click.echo(f"Warning: --in_file not provided. Using `{default_file}` as per `exp_id`.")
        return default_file
    return value

@r2e.command()
@click.option('--exp-id', '-e', default="temp", help="The experiment ID used for the test execution")
@click.option('--function', '-f', default=None, help="Name of the function to show.")
@click.option('--in-file', '-i', callback=_default_in_file_exec, help="The input file for the test execution")
@exec_options
def execute(**kwargs):
    """Execute the generated equivalence tests."""
    
    if kwargs['local']:
        click.echo(f"Note: Running the execution service locally. Remove --local for docker.")
        kwargs['image'] = "r2e:temp"
    elif not kwargs['image']:
        click.echo(f"Warning: --image not provided. Using `r2e:{kwargs['exp_id']}` as per `exp_id`.")
        kwargs['image'] = f"r2e:{kwargs['exp_id']}"
    elif kwargs['image'] == "r2e:temp":
        click.echo("Warning: Using the default image `r2e:temp`. Use --image for custom image.")
    else:
        click.echo(f"Note: Using the provided image: {kwargs['image']}")
    
    testgen_file_path = os.path.join(TESTGEN_DIR, kwargs['in_file'])
    if not os.path.exists(testgen_file_path):
        click.echo(f"\nNo generated tests found for experiment ID: {kwargs['exp_id']}")
        return
        
    args = ExecutionArgs(**kwargs)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    EquivalenceTestRunner.run(args)
    click.echo("Test execution completed successfully.")
    show_result_file(os.path.join(EXECUTION_DIR, f"{args.exp_id}_out.json"))


################### r2e genexec ###################

@r2e.command()
@click.option('--exp-id', '-e', default="temp", help="The experiment ID used for the test execution")
@click.option('--function', '-f', default=None, help="Name of the function to show.")
@click.option('--in-file', '-i', callback=_default_in_file_gen, help="The input file for the genexec agent.")
@click.option('--max_rounds', '-k', default=3, type=int, help="The maximum number of rounds to run the genexec process")
@click.option('--min-cov', default=0.8, type=float, help="The minimum branch coverage to consider a test valid")
@click.option('--min-valid', default=0.8, type=float, help="The minimum percentage of valid problems to achieve in the dataset")
@gen_options
@llm_options
@exec_options
def genexec(**kwargs):
    """Generate-and-Execute Agent that iteratively generates and executes tests."""
    
    if kwargs['local']:
        click.echo(f"Note: Running the execution service locally. Remove --local for docker.")
        kwargs['image'] = "r2e:temp"
    elif not kwargs['image']:
        click.echo(f"Warning: --image not provided. Using `r2e:{kwargs['exp_id']}` as per `exp_id`.")
        kwargs['image'] = f"r2e:{kwargs['exp_id']}"
    elif kwargs['image'] == "r2e:temp":
        click.echo("Warning: Using the default image `r2e:temp`. Use --image for custom image.")
    else:
        click.echo(f"Note: Using the provided image: {kwargs['image']}")
    
    args = GenExecArgs(**kwargs)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    R2EGenExec.genexec(args)
    show_result_file(os.path.join(EXECUTION_DIR, f"{args.exp_id}_out.json"))


################### r2e list-functions ###################

def extract_signature_and_docstring(code, max_width=100):
    try:
        tree = ast.parse(code)
        function_def = tree.body[0]
        args = [arg.arg for arg in function_def.args.args] # type: ignore
        defaults = [ast.unparse(default) for default in function_def.args.defaults] # type: ignore
        padded_defaults = [''] * (len(args) - len(defaults)) + defaults
        signature = ', '.join(f'{arg}={default}' if default else arg for arg, default in zip(args, padded_defaults))
        docstring = ast.get_docstring(function_def) # type: ignore
        if docstring:
            docstring = textwrap.shorten(docstring, width=max_width, placeholder="...")
        else:
            docstring = "No docstring available"  
        return signature, docstring
    except:
        return "Could not parse signature", "Could not parse docstring"

def get_func_info(func):
    try:
        full_name = f"{func.name}" if isinstance(func, Function) else f"{func.class_name}.{func.name}"
    except:
        full_name = func.name

    signature, docstring = extract_signature_and_docstring(func.code)
    ftype = "Function" if isinstance(func, Function) else "Method"
    return full_name, signature, docstring, ftype


@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for prefixing the extracted functions file")
@click.option('--limit', '-l', default=10, type=int, help="The maximum number of functions to list")
@click.option('--detailed', '-d', is_flag=True, default=False, help="Show detailed information for each function")
def list_functions(exp_id, detailed, limit):
    """List the extracted functions and methods."""
    file_path = os.path.join(EXTRACTED_DATA_DIR, f"{exp_id}_extracted.json")
    
    if not os.path.exists(file_path):
        click.echo(f"No extracted functions found for experiment ID: {exp_id}")
        return

    functions = load_functions(file_path)
    click.echo(f"Total extracted functions/methods: {len(functions)}")

    for i, func in enumerate(functions[:limit], 1):
        full_name, signature, docstring, ftype = get_func_info(func)
        if detailed:
            click.echo(f"\n{i}. {ftype}: {full_name}")
            click.echo(f"   File: {func.file.relative_file_path}")
            click.echo(f"   Signature: {func.name}({signature})")
            click.echo(f"   Docstring: {docstring}")
        else:
            click.echo(f"{i}. {full_name} ({func.file.relative_file_path}) [{ftype}]")

    if len(functions) > limit:
        click.echo(f"\n... and {len(functions) - limit} more functions/methods. Use --limit to list more.")

    if not detailed:
        click.echo("\nUse --detailed or -d for more information about each function.")
                    
    
################### r2e show ###################

@r2e.command()
@click.option('--exp_id', '-e', default="temp", help="Experiment ID used for prefixing the extracted functions file")
@click.option('--fname', '-f', required=False, help="Name of the function to show.")
@click.option('--code', '-c', is_flag=True, help="Show the code of the function.")
@click.option('--test', '-t', is_flag=True, help="Show the generated test for the function.")
@click.option('--result', '-r', is_flag=True, help="Show the generated test for the function.")
@click.option('--show-all', '-a', is_flag=True, help="Show (code, test, result) for function(s).")
# additional options
@click.option('--chat', is_flag=True, help="Show the chat messages leading up to the final test for a function.")
@click.option('--summary', is_flag=True, help="Show an overall summary of the test execution results.")
def show(exp_id, fname, code, test, result, show_all, chat, summary):
    """Show detailed information about a specific function."""
    if not summary and not fname:
        click.secho("Error: Please provide the name of the function using --fname.", fg="red")
        return
    
    extracted_file_path = os.path.join(EXTRACTED_DATA_DIR, f"{exp_id}_extracted.json")
    testgen_file_path = os.path.join(TESTGEN_DIR, f"{exp_id}_generate.json")
    executed_file_path = os.path.join(EXECUTION_DIR, f"{exp_id}_out.json")
    
    if summary:
        if not os.path.exists(executed_file_path):
            click.echo(f"\nNo executed tests found for experiment ID: {exp_id}")
            return

        click.echo(summarize(exp_id))
        return
    
    if not os.path.exists(extracted_file_path):
        click.echo(f"No extracted functions found for experiment ID: {exp_id}")
        return

    functions = load_functions(extracted_file_path)
    target_function = next((func for func in functions if func.name == fname), None)
    if not target_function:
        click.echo(f"No function named '{fname}' found in the extracted data.")
        return
    
    full_name, signature, docstring, ftype = get_func_info(target_function)
    click.echo(f"{ftype}: {full_name}")
    click.echo(f"File: {target_function.file.file_path}")
    
    if code or show_all:
        click.echo("Code:\n")
        click.echo(textwrap.indent(target_function.code, '    '))
    
    if test or show_all:
        if not (os.path.exists(testgen_file_path) or os.path.exists(executed_file_path)):
            click.echo(f"\nNo generated tests found for experiment ID: {exp_id}")
            return

        if os.path.exists(executed_file_path):
            functions_under_test = load_functions_under_test(executed_file_path)
        else:
            functions_under_test = load_functions_under_test(testgen_file_path)
            
        target_fut = next((fut for fut in functions_under_test if fut.name == fname), None)
        
        if not target_fut:
            if os.path.exists(testgen_file_path):
                functions_under_test = load_functions_under_test(testgen_file_path)
                target_fut = next((fut for fut in functions_under_test if fut.name == fname), None)
            else:
                click.echo(f"\nNo generated test found for function '{fname}'.")
                return

        click.echo("\nGenerated Test:")

        for test_name, test_code in target_fut.test_history.latest_tests.items(): # type: ignore
            click.echo(f"\n{test_name}:")
            click.echo(textwrap.indent(test_code, '    '))
        
    if result or show_all:
        if not os.path.exists(executed_file_path):
            click.echo(f"\nNo executed tests found for experiment ID: {exp_id}")
            return

        executed_futs = load_functions_under_test(executed_file_path)
        target_executed_fut = next((fut for fut in executed_futs if fut.name == fname), None)
        
        if not target_executed_fut:
            click.echo(f"\nNo executed test found for function '{fname}'.")
            return

        click.echo("\nTest Results:")

        for test_name, results in target_executed_fut.exec_stats['run_tests_logs'].items(): # type: ignore
            click.echo(f"\n{test_name}:")
            click.echo(json.dumps(results, indent=4))
            click.echo(json.dumps(target_executed_fut.coverage, indent=4))
    
    if chat or show_all:
        if not os.path.exists(executed_file_path):
            click.echo(f"\nNo executed tests found for experiment ID: {exp_id}")
            return

        executed_futs = load_functions_under_test(executed_file_path)
        target_executed_fut = next((fut for fut in executed_futs if fut.name == fname), None)
        
        if not target_executed_fut:
            click.echo(f"\nNo executed test found for function '{fname}'.")
            return

        click.echo("\nChat Messages:")
        chat_messages = target_executed_fut.test_history.latest_chat_messages
        
        if not chat_messages:
            click.echo("No chat messages found.")
            return
        
        for message in chat_messages:
            click.secho(f"{message['role'].capitalize()}:", fg="green")
            truncated_content = '\n'.join(message['content'].split('\n')[:50])
            click.echo(truncated_content)

if __name__ == '__main__':
    r2e()
