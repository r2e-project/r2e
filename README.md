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

Find the complete CLI documentation at [CLI.md](./docs/CLI.md). Below is a quickstart guide:


### 1. Setup and Extract

First, choose a unique experiment id (e.g., `quickstart`) that you can reuse for the entire workflow. Then setup repositories and extract functions from:
```posh
r2e setup -r https://github.com/google-research/python-graphs
r2e extract -e quickstart --overwrite_extracted
```
<details>
<summary><code>Output</code></summary>

```
Cloning repository https://github.com/google-research/python-graphs
Repo Location: /home/user/buckets/local_repoeval_bucket/repos/
Setup completed successfully.

Result: /home/user/buckets/local_repoeval_bucket/repos

Extracting..: 100%|███████████████████████| 2/2 [00:00<00:00,  8.89it/s]
Extracted 18 functions and 53 methods
Extraction completed successfully.

Result: /home/user/buckets/r2e_bucket/extracted_data/quickstart_extracted.json
```
</details>

> [!Note]
> We also support copying from a local path, or processing a list of URLs/local paths from a json file ([cli docs](./docs/CLI.md)).
>
> During extraction all repos cloned into REPOS_DIR are processed. The extracted functions and methods are written to a JSON file. Use `--overwrite_extracted` to overwrite any existing results.


### 2. Build and Install

**Docker Mode:** By default, all repos in REPOS_DIR are installed in a Docker image for sandboxed execution. Find the generated dockerfile in REPOS_DIR. Useful reference: [install docker](http://docs.docker.com/engine/install/)

**Local Mode:** Use `--local` which will suggest the steps ***you need to take to manually*** to install repos.

```posh
r2e build -e quickstart
```
<details>
<summary><code>Output</code></summary>

```
Found 1 repositories in the repos directory.
Running in Docker mode.
Creating a dockerfile...
Dockerfile generated at:  /local_repoeval_bucket/repos/r2e_final_dockerfile.dockerfile
...

[+] Building 553.2s (16/16) FINISHED                                         docker:default
 => [internal] load build definition from r2e_final_dockerfile.dockerfile              0.0s
 => => transferring dockerfile: 2.52kB                                                 0.0s
 ...
 => exporting to image                                                                31.0s 
 => => exporting layers                                                               30.9s 
 => => writing image sha256:28d6f5751dfac6de9ccd883f0830cf8ac5c88e46df8bd7             0.0s 
 => => naming to docker.io/library/r2e:quickstart                                      0.0s

$ docker image ls
REPOSITORY   TAG          IMAGE ID       CREATED         SIZE
r2e          quickstart   28d6f5751dfa   4 minutes ago   10.1GB
```
</details>


### 3. Generate and Execute Tests

R2E provides a single command that runs a series of `k` generate-execute rounds w/ feedback. The loop continues until `min_valid`% functions reach a `min_cov`% branch coverage. Defaults: `k=3`, `min_valid=0.8`, and `min_cov=0.8`.

```posh
r2e genexec -e quickstart --save_chat
```
<details>
<summary><code>Output</code></summary>

```
Generating contexts: 100%|███████████████████████| 10/10 [00:03<00:00, 20.56it/s]

Starting round 1/3
100%|███████████████████████| 10/10 [00:13<00:00,  1.36s/it]
Loaded 10 functions under test
100%|███████████████████████| 10/10 [00:01<00:00,  5.74it/s]
Round 1 completed. Status: 0.20 good FUTs.

Starting round 2/3
100%|███████████████████████| 8/8 [00:20<00:00,  2.58s/it]
Loaded 8 functions under test
100%|███████████████████████| 8/8 [00:01<00:00,  4.66it/s]
Round 2 completed. Status: 0.60 good FUTs.

Starting round 3/3
100%|███████████████████████| 4/4 [00:13<00:00,  3.39s/it]
Loaded 4 functions under test
100%|███████████████████████| 4/4 [00:01<00:00,  2.41it/s]
Reached max rounds. Stopping at round 3

Result: /home/user/buckets/r2e_bucket/execution/quickstart_out.json
```
</details>

> [!Note]
> You can also run `r2e generate` and `r2e execute` separately ([cli docs](./docs/CLI.md)).
>
> The generated tests are executed in the Docker container. Use `--local` to execute locally.


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
