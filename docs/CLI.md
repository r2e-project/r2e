# R2E CLI Documentation

## Summary:

- [r2e setup](#r2e-setup): Set up the environment and clone repositories.
- [r2e build](#r2e-build): Build a Docker image for your experiment.
- [r2e extract](#r2e-extract): Extract functions and methods from repositories.
- [r2e generate](#r2e-generate): Generate equivalence tests for the extracted functions.
- [r2e execute](#r2e-execute): Execute the generated equivalence tests.
- [r2e genexec](#r2e-genexec): Generate-and-Execute Agent that iteratively generates and executes tests.
- [r2e list-functions](#r2e-list-functions): List the extracted functions and methods.
- [r2e show](#r2e-show): Show detailed information about a specific function.

## `r2e setup`

Set up the environment and clone repositories.

### Options:

- `--repo_url`: URL of the repository to build
- `--local_repo_path`: Path to the local repository
- `--repo_paths_file`: Path to a json file containing a list of local paths
- `--repo_urls_file`: Path to a json file containing a list of URLs
- `--cloning_multiprocess`: Number of processes to use for cloning the repositories (default: 16)
- `--run_pycg`: Whether to run PyCG on the repositories
- `--pycg_timeout`: Timeout for PyCG in minutes (default: 5)
- `--pycg_multiprocess`: Number of processes to use for running PyCG (default: 16)

## `r2e build`

Build a Docker image for your experiment.

### Options:

- `--exp_id`: Experiment ID used for identifying the Docker image (default: temp)
- `--local`: Whether to run the build locally. Default is building a Docker image.
- `--install_batch_size`: Number of repositories to install in parallel in the Docker container. (default: 10)

## `r2e extract`

Extract functions and methods from repositories.

### Options:

- `--exp_id`: Experiment ID used for prefixing the extracted functions and methods (default: temp)
- `--overwrite_extracted`: Whether to overwrite the extracted functions and methods
- `--extraction_multiprocess`: Number of processes to use for extracting functions and methods (default: 16)
- `--disable_dunder_methods`: Disable dunder method filter
- `--disable_no_docstring`: Disable functions w/o docstring filter
- `--disable_signature_filters`: Disable function signature filters (args, returns)
- `--disable_keyword_filters`: Disable keyword filters (docstring, body, name)
- `--disable_wrapper_filters`: Disable filters for wrappers (decorators, etc.)
- `--disable_lines_filter`: Disable lines filter
- `--disable_all_filters`: Disable all filters

## `r2e generate`

Generate equivalence tests for the extracted functions.

### Options:

- `--exp_id`: Experiment ID used for prefixing the generated tests file (default: temp)
- `--function`: Name of the function to show.
- `--in_file`: The input file for the test generator. Defaults to {exp_id}_extracted.json if not provided.
- `--context_type`: The context type to use for the language model (default: sliced)
- `--oversample_rounds`: The number of rounds to oversample (default: 1)
- `--max_context_size`: The maximum context size (default: 6000)
- `--save_chat`: Whether to save the chat messages
- `--multiprocess`: The number of processes to use for multiprocessing (default: 8)
- `--model_name`: The model name to use for the language model (default: gpt-4-turbo-2024-04-09)
- `--n`: The number of completions to generate (default: 1)
- `--top_p`: The nucleus sampling probability (default: 0.95)
- `--max_tokens`: The maximum number of tokens to generate (default: 1024)
- `--temperature`: The temperature for the LLM request (default: 0.2)
- `--presence_penalty`: The presence penalty for the LLM request
- `--frequency_penalty`: The frequency penalty for the LLM request
- `--stop`: The stop sequence for the LLM request
- `--openai_timeout`: The timeout for the OpenAI API request (default: 60)
- `--use_cache`: Whether to use the cache for LLM queries. Default is True. (default: True)
- `--cache_batch_size`: The batch size for cache writes. (default: 30)

## `r2e execute`

Execute the generated equivalence tests.

### Options:

- `--exp_id`: The experiment ID used for the test execution (default: temp)
- `--function`: Name of the function to show.
- `--in_file`: The input file for the test execution
- `--local`: Whether to run the execution service locally. Default is docker.
- `--image`: The name of the docker image in which to run the tests (default: r2e:temp)
- `--execution_multiprocess`: The number of processes to use for executing the functions and methods (default: 20)
- `--port`: The port to use for the execution service. Default is 3006 for sequential execution. For parallel, port is randomly picked. (default: 3006)
- `--timeout_per_task`: The timeout for the execution service to complete one task in seconds (default: 180)
- `--batch_size`: The number of functions to run before writing the output to the file (default: 100)

## `r2e genexec`

Generate-and-Execute Agent that iteratively generates and executes tests.

### Options:

- `--exp_id`: The experiment ID used for the test execution (default: temp)
- `--function`: Name of the function to show.
- `--in_file`: The input file for the genexec agent.
- `--max_rounds`: The maximum number of rounds to run the genexec process (default: 3)
- `--min_cov`: The minimum branch coverage to consider a test valid (default: 0.8)
- `--min_valid`: The minimum percentage of valid problems to achieve in the dataset (default: 0.8)
- `--context_type`: The context type to use for the language model (default: sliced)
- `--oversample_rounds`: The number of rounds to oversample (default: 1)
- `--max_context_size`: The maximum context size (default: 6000)
- `--save_chat`: Whether to save the chat messages
- `--multiprocess`: The number of processes to use for multiprocessing (default: 8)
- `--model_name`: The model name to use for the language model (default: gpt-4-turbo-2024-04-09)
- `--n`: The number of completions to generate (default: 1)
- `--top_p`: The nucleus sampling probability (default: 0.95)
- `--max_tokens`: The maximum number of tokens to generate (default: 1024)
- `--temperature`: The temperature for the LLM request (default: 0.2)
- `--presence_penalty`: The presence penalty for the LLM request
- `--frequency_penalty`: The frequency penalty for the LLM request
- `--stop`: The stop sequence for the LLM request
- `--openai_timeout`: The timeout for the OpenAI API request (default: 60)
- `--use_cache`: Whether to use the cache for LLM queries. Default is True. (default: True)
- `--cache_batch_size`: The batch size for cache writes. (default: 30)
- `--local`: Whether to run the execution service locally. Default is docker.
- `--image`: The name of the docker image in which to run the tests (default: r2e:temp)
- `--execution_multiprocess`: The number of processes to use for executing the functions and methods (default: 20)
- `--port`: The port to use for the execution service. Default is 3006 for sequential execution. For parallel, port is randomly picked. (default: 3006)
- `--timeout_per_task`: The timeout for the execution service to complete one task in seconds (default: 180)
- `--batch_size`: The number of functions to run before writing the output to the file (default: 100)

## `r2e list-functions`

List the extracted functions and methods.

### Options:

- `--exp_id`: Experiment ID used for prefixing the extracted functions file (default: temp)
- `--limit`: The maximum number of functions to list (default: 10)
- `--detailed`: Show detailed information for each function

## `r2e show`

Show detailed information about a specific function.

### Options:

- `--exp_id`: Experiment ID used for prefixing the extracted functions file (default: temp)
- `--fname`: Name of the function to show.
- `--code`: Show the code of the function.
- `--test`: Show the generated test for the function.
- `--result`: Show the generated test for the function.
- `--show_all`: Show (code, test, result) for function(s).
- `--chat`: Show the chat messages leading up to the final test for a function.
- `--summary`: Show an overall summary of the test execution results.

