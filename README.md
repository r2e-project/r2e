<p align="center">
  <a href="https://www.r2e.dev">
    <img src="assets/images/r2e-banner.png" alt="r2e.dev" />
  </a>
</p>


<div align="center">

  [![Website](https://img.shields.io/badge/website-r2e.dev-blue)](https://r2e.dev)
  [![Paper](https://img.shields.io/badge/paper-ICML%202024-purple)](https://r2e.dev/pdfs/paper.pdf)
  [![Demos](https://img.shields.io/badge/youtube-demos-maroon)](https://www.youtube.com/watch?v=NrTEbwyofAg&list=PLA_lMIaJefMZyZOac67rxwRSjmE8rNZ9v)
  [![GitHub license](https://img.shields.io/badge/License-MIT-blu.svg)](https://lbesson.mit-license.org/)
</div>

---

[R2E](https://r2e.dev) (Repository to Environment) is a framework that turns *any* GitHub repository into an executable environment for evaluating static code generation models and programming agents at scale. It extracts functions and methods from the repository, generates and executes **equivalence tests** for them using LLMs, and creates an interactive execution environment. These environments can be used to evaluate the quality of LLM generated code.


## Installation

1. Install [`uv`](https://docs.astral.sh/uv/) to setup R2E.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a venv, clone, and install.
```bash
git clone https://github.com/r2e-project/r2e.git
cd r2e && uv venv && source .venv/bin/activate
uv sync
```

## Key Concept: Equivalence Test Harnesses

R2E introduces **Equivalence Tests**, a test that checks if two pieces of code are equivalent. In the context of R2E, an **Equivalence Test** checks if the output of a function/method in a repository is the same as the output of the generated code for the same function/method. Here's an overview of the key principles of R2E:

| **Principle** | **Description** |
|---------------|-----------------|
| **Equivalence Tests** | R2E generates tests that use the ground truth implementation to check equivalence, avoiding predicting test outputs.|
| **Complete Harness** | Generates harnesses with complete setup info (e.g., files, DB connections) instead of simple I/O examples. |
| **Sliced Context** | Leverages dependency slicing to provide minimal, relevant context, for test generation. |
| **Coverage**  | Filters incorrect tests and assesses test quality using branch coverage.|

Find more details and examples at [r2e.dev](https://r2e.dev) and in our [paper](https://r2e.dev/pdfs/paper.pdf).


## Usage

R2E provides a convenient CLI to work with. The usual steps are as follows: 
(1) [setup and extract functions from repositories](#1-setup-and-extract), 
(2) [build and install repositories](#2-build-and-install), and
(3) [generate and execute **Equivalence Tests**](#3-generate-and-execute-tests)

<!-- Find the complete CLI documentation at [./docs/cli.md](./docs/cli.md). -->

<!-- Note: R2E uses a custom testing framework [R2E Test Server](https://github.com/r2e-project/r2e-test-server) that provides an interface for agents to interact with the built environment and execute arbitrary code. -->

### 1. Setup and Extract

#### 1.1 Setup Repositories

Use the following command to clone and setup repositories. 
```bash
r2e setup --repo_url https://github.com/google-research/python-graphs
```

> [!Note]
> We also support cloning from a URL, copying from a local path, or processing a list of URLs or local paths from a json file.

#### 1.2 Extract Functions and Methods
To extract functions and methods, use the following command. First choose an **experiment ID** for your run that you will reuse in all subsequent steps.

```bash
r2e extract --exp_id <experiment_id> --overwrite_extracted
```

> [!Note]
> The script will find all directories in the REPOS_DIR directory (where your repos were cloned), and extract functions and methods from them. The extracted functions and methods are written to a JSON file in the EXTRACTION_DIR directory. If the extraction file already exists, the script will not overwrite it unless you set --overwrite_extracted to True.


### 2. Build and Install

R2E builds and installs the repositories in a Docker image. This image is used to execute the generated tests in the next step.
```bash
r2e build --exp_id <experiment_id> --install_batch_size <num parallel installs>
```

> [!Note]
> The dockerfile will copy all the directories in the REPOS_DIR directory (where your repos were cloned) to the Docker image. It will then install the repositories using a combination of [`pdm`](pdm-project.org) and `pip` install commands. The Docker image is stored in the [docker_builder](./r2e/repo_builder/docker_builder) directory.

> [!Tip]
> Please follow [http://docs.docker.com/engine/install/](http://docs.docker.com/engine/install/) for instructions on installing docker. It is recommended to follow the post-installation steps to run docker as a non-root user. 

### 3. Generate and Execute Tests

#### 3.1 Generation
```bash
r2e generate --exp_id <experiment_id>
```

> [!Note]
> This generates the **equivalence tests** for the functions/methods in the input JSON file. R2E generates the tests using a combination of static analysis and prompting language models. Several other args are available to control the generation process and language model in [testgen/args.py](./r2e/generators/testgen/args.py).

#### 3.2 Execution
```bash
r2e execute --exp_id <experiment_id> 
```

> [!Note]
> The script will execute the generated tests in the Docker container. The results are stored in the [EXECUTION_DIR] directory. 


#### 3.3 Evaluation
```bash
r2e show --exp_id <experiment_id> --summary
```

> [!Note]
> This would give you a summary of the generated tests and their execution results. The evaluator also provides a detailed breakdown of the execution results for each test.


## Additional Resources

1. **Improving Specifications:**: Find details about improving the specifications of extracted functions to build benchmarks using LLMs @ [Spec Refinement](./r2e/generators/specgen/README.md).

2. **PAT: Program Analysis Tools**: We developed an in-house program and static analysis toolbox that powers R2E along with LLMs. These tools can be used independently too. Learn more about them @ [PAT](./r2e/pat/README.md).

## Citation

If you use R2E in your research, please cite the following paper:

```bibtex
@inproceedings{
    jain2024r2e,
    title={R2E: Turning any Github Repository into a Programming Agent Environment},
    author={Naman Jain and Manish Shetty and Tianjun Zhang and King Han and Koushik Sen and Ion Stoica},
    booktitle={ICML},
    year={2024},
}
```
