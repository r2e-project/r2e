# Spec Refinement

Relevant Code: [SpecGenerator](./src/r2e/generators/specgen/generate.py)

While the user is free to choose the extracted functions to benchmark code LLMs and programming agents, we provide some tools and strategies to build robust benchmarks based on our study.

**Improving Specifications:** We believe that natural language docstrings in GitHub repos might
be ambiguous or under-specified for use in code generation. We provide an automated approach to refine these docstrings using language models by providing them useful information on the observed behavior of the function when executed using the generated test harness
```bash
python r2e/generators/specgen/generate.py
    -i <input_json> 
    --exp_id <experiment_id>  
    --multiprocess <num_processes>
    --cache_batch_size <batch_size_for_caching_llm_calls>
```

> [!Note]
>
> The input file must be functions that _have been executed_ using tests from the previous section. The results of execution, such as I/O examples, type signatures, etc., are provided to the LLM for refinement. More details on this in our [paper](r2e.dev/pdfs/r2e_paper.pdf).