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
```posh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a venv, clone, and install.
```posh
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

Setup repositories in R2E's workspace and extract functions and methods from them.
```posh
r2e setup --repo_url https://github.com/google-research/posh-graphs
r2e extract --exp_id quickstart --overwrite_extracted
```
<details>
<summary><code>Output</code></summary>

```
...
```
</details>

> [!Note]
> We also support copying from a local path, or processing a list of URLs/local paths from a json file.
>
> During extraction all repos cloned into REPOS_DIR are processed. The extracted functions and methods are written to a JSON file in the EXTRACTION_DIR directory. Use `--overwrite_extracted` to overwrite any existing results.


### 2. Build and Install

**Docker Mode:** By default, all repos in REPOS_DIR are installed in a Docker image for sandboxed execution. Find the generated dockerfile in REPOS_DIR. Useful reference: [installing docker](http://docs.docker.com/engine/install/)
```posh
r2e build --exp_id quickstart
```
<details>
<summary><code>Output</code></summary>

```
...
```
</details>

**Local Mode:** Use `--local` which will suggest the steps ***you need to take to manually*** to install repos.
```posh
r2e build --exp_id quickstart --local
```
<details>
<summary><code>Output</code></summary>

```
...
```
</details>

### 3. Generate and Execute Tests

```posh
r2e generate --exp_id quickstart
```

#### 3.2 Execution
```posh
r2e execute --exp_id quickstart 
```

> [!Note]
> The generated tests in the Docker container. Use `--local` to execute locally.
> The results are stored in the [EXECUTION_DIR] directory.


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
