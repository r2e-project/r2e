# PAT: Program Analysis Tools

This directory contains the source code for the program analysis tools that are provided by R2E.

These tools are programmable editor interface for agents to interact with codebases and perform various program analysis tasks.
These tools go well beyond the capabilities of traditional LSPs and linters, and are designed to be used by agents to perform more complex program analysis tasks.
The results of these tools can used by programming agents to make more informed decisions about the codebase.

> Note: More information on the individual tools soon... 🚧

## 🧰 The Toolbox
- [`AST`](./ast/): Tools for working with Abstract Syntax Trees.
- [`Callgraphs`](./callgraph/): Tools for working with callgraphs.
- [`Imports`](./imports/): Tools for analyzing and using import statements.
- [`Modules`](./modules/): Tools for working with python modules.
- [`Slicers`](./dependency_slicer/): Tools for slicing dependencies.
- [`Instrumentation`](./instrument/): Tools for instrumenting code.


> Further, if you are looking for how R2E's generated environments can be used or how R2E runs tests, please refer to the [R2E-test-server](https://github.com/r2e-project/r2e-test-server) repository.
> - This repo contains the code to setup a test server for running tests
> - It can be installed using a `pip install r2e-test-server`
> - More information on it here: [How to use environments]().