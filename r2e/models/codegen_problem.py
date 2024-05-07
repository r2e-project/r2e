from r2e.models.fut import FunctionUnderTest, MethodUnderTest


class CodeGenProblem:
    """Represents a code generation problem"""

    spec: str


class CodeGenProblemFunction(CodeGenProblem, FunctionUnderTest):
    @classmethod
    def from_fut_and_spec(cls, fut: FunctionUnderTest, spec: str):
        fut_dump = fut.model_dump()
        fut_dump.update({"spec": spec})
        return cls(**fut_dump)


class CodeGenProblemMethod(CodeGenProblem, MethodUnderTest):
    @classmethod
    def from_mut_and_spec(cls, mut: MethodUnderTest, spec: str):
        mut_dump = mut.model_dump()
        mut_dump.update({"spec": spec})
        return cls(**mut_dump)


def create_codegen_problem(obj: FunctionUnderTest | MethodUnderTest, spec: str):
    if isinstance(obj, FunctionUnderTest):
        return CodeGenProblemFunction.from_fut_and_spec(obj, spec)
    elif isinstance(obj, MethodUnderTest):
        return CodeGenProblemMethod.from_mut_and_spec(obj, spec)
    else:
        raise ValueError("Unknown input type")
