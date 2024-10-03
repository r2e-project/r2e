def extract_codeblock(output) -> str:
    outputlines = output.split("\n")
    indexlines = [i for i, line in enumerate(outputlines) if "```" in line]
    if len(indexlines) < 2:
        return ""
    return "\n".join(outputlines[indexlines[0] + 1 : indexlines[1]])


def get_generated_tests(outputs) -> list[str]:
    # NOTE: only a single sampled output from the model
    outputs = [output[0] for output in outputs]

    code_blocks = []
    for output in outputs:
        code = extract_codeblock(output)
        code_blocks.append(code)
    return code_blocks
