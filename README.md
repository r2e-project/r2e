<p align="center">
  <a href="https://www.r2e.dev">
    <img src="assets/images/r2e-banner.png" alt="r2e.dev" />
  </a>
</p>


<p align="center">
  <a href="https://r2e.dev"><strong>🌐 Website & Demos</strong></a>&nbsp; | &nbsp;
  <a href="https://r2e.dev/pdfs/paper.pdf"><strong>📄 Paper @ ICML 2024</strong></a>&nbsp; | &nbsp;
  <a href=""><strong>🤗 Datasets (coming soon!)</strong></a>&nbsp;
</p>

---


## Overview

This is the code for the [R2E framework](https://r2e.dev). 
Building a scalable and interactive testbed for evaluating general-purpose AI programming agents
for real-world code has been challenging, particularly due to a lack of high-quality test suites
available.

![Overview](./assets/images/overview.png)

## Features

- Convert any GitHub repository into an executable environment
- Generate equivalence tests for functions and methods
- Execute tests in Docker containers or locally
- Evaluate code generation models and programming agents at scale

## Installation

### Prerequisites

- Python 3.11+
- Docker (optional, for full functionality)

### Steps

1. Create a virtual environment (optional) w/ Python 3.11+. For example, using conda:
   ```bash
   conda create -n r2e-env python=3.11
   conda activate r2e-env
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/r2e-project/r2e.git
   cd r2e
   ```

3. Install using poetry (recommended) or pip:
   ```bash
   pip install poetry
   poetry install
   ```
   Or with just pip:
   ```bash
   pip install -e .
   ```

## Usage

R2E can be used **locally** or with **Docker** for full functionality.

### Quickstart (Local)

For a quick start guide to using R2E locally, see our [Quickstart Guide](docs/quickstart.md).

### Full Usage (Docker)

For comprehensive instructions on using R2E with Docker for full functionality, see our [Full Guide](docs/fullguide.md).


## Citation

If you use R2E in your research, please cite our paper:

```bibtex
@inproceedings{
    jain2024r2e,
    title={R2E: Turning any Github Repository into a Programming Agent Environment},
    author={Naman Jain and Manish Shetty and Tianjun Zhang and King Han and Koushik Sen and Ion Stoica},
    booktitle={ICML},
    year={2024},
}
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [MIT License](LICENSE).

For more details on the R2E project, refer to [r2e.dev](https://r2e.dev)!