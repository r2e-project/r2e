import click
from r2e.cli import r2e  # Import your main CLI group


def generate_docs():
    output = "# R2E CLI Documentation\n\n"

    # Generate Table of Contents
    output += "## Summary:\n\n"
    for command in r2e.commands.values():
        assert command.name is not None, "Command name must be defined"
        output += (
            f"- [r2e {command.name}](#r2e-{command.name.lower()}): {command.help}\n"
        )
    output += "\n"

    for command in r2e.commands.values():
        output += f"## `r2e {command.name}`\n\n"
        output += f"{command.help}\n\n" # type: ignore
        output += "### Options:\n\n"

        for param in command.params:
            output += f"- `--{param.name}`: {param.help}" # type: ignore
            if param.default:
                output += f" (default: {param.default})"
            output += "\n"

        output += "\n"

    with open("./docs/CLI.md", "w") as f:
        f.write(output)


if __name__ == "__main__":
    generate_docs()
