# R2E / Repo Builder

This is a simple tool to sets up and builds repositories to be used in R2E environments. First, the repositories are cloned or copied to a relevant directory where corresponding call-graphs are built. Next, various heuristics are applied to extract a set of functions or methods that can be viable for the application (like code generation). [r2e/repo_builder/fut_extractor](r2e/repo_builder/fut_extractor) files implement these various heuristics which can be modified based on requirements. Finally, the repositories are moved to a bucket where they are buildtusing a combination of `pip` and [`pdm`](pdm-project.org) which allows caching packages across repositories. 


## Cloning Repositories and Building Call Graphs
We support providing the set of repositories to be cloned or copied in the following four ways. 

```sh
# single repo mode
python r2e/repo_builder/setup_repos.py --repo_url {github_url}
python r2e/repo_builder/setup_repos.py --local_repo_path {path_to_local_repo_dir}

# batch mode
python r2e/repo_builder/setup_repos.py --repo_urls_file {json_file_with_repo_urls}
python r2e/repo_builder/setup_repos.py --repo_paths_file {json_file_with_repo_paths}
```

## Extracting Functions and Methods
Next, the following command extracts functions and methods from the repositories. 

```sh
python r2e/repo_builder/extract_func_methods.py --exp_id {exp_id_to_save_extracted_results}
```

## Building Repositories
Finally, the repositories are built and stored in a docker image that can be containerized for generating an R2E environment. First, we will construct a dockerfile based on the repos_dir in [`config.yml`](config.yml).

```sh
python r2e/repo_builder/docker_builder/r2e_dockerfile_builder.py --install_batch_size {num_repos_to_build_in_parallel}
```

This will construct `r2e/repo_builder/docker_builder/r2e_final_dockerfile.dockerfile` file which can be used to build the docker image. You can follow installation instructions on [http://docs.docker.com/engine/install/](http://docs.docker.com/engine/install/). Remember to follow the post-installation steps to run docker as a non-root user. Once docker is installed on your system, you can run the following command to build the docker image. 

```sh
docker build --network=host  -t {image_name} -f {path_to_dockerfile} .
```

Note that you need to run this command from within repos_dir due to issues with using absolute paths in `COPY` [docker-copy-from-ubuntu-absolute-path](https://stackoverflow.com/questions/47012495/docker-copy-from-ubuntu-absolute-path). You can modify line 27 of resulting dockerfile `COPY . /repos` appropirately if you don't want to run from within repos_dir.
