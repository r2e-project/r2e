import ast
from enum import Enum
from collections import defaultdict

from r2e.pat.dependency_slicer.ast_statements import AstStatement


class DependencySliceUnparseEnum(Enum):
    MARKDOWN_FILES = "markdown_files"
    PATH_COMMENT = "path_comment"


class DependencyGraphEdge:
    def __init__(self, vertex1: AstStatement, vertex2: AstStatement, symbol: str):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.symbol = symbol

    def __str__(self):
        return f"{self.vertex2} ({self.symbol})"


class DependencyGraph:
    def __init__(self, inputstmts: list[AstStatement]):
        self._adjacency_list: dict[AstStatement, list[DependencyGraphEdge]] = (
            defaultdict(list)
        )
        self.file_path_adjacency_list: dict[str, list[str]] = defaultdict(list)
        self._inputstmts = inputstmts
        self._repo_path = inputstmts[0].file.repo.repo_path

    def add_edge(
        self, vertex1: AstStatement, vertex2: AstStatement, symbol: str
    ) -> None:
        edge = DependencyGraphEdge(vertex1, vertex2, symbol)
        self._adjacency_list[vertex1].append(edge)

        vertex1_file_path = vertex1.file_path
        vertex2_file_path = vertex2.file_path
        if vertex1_file_path != vertex2_file_path:
            self.file_path_adjacency_list[vertex1_file_path].append(vertex2_file_path)
        elif len(self.file_path_adjacency_list) == 0:
            self.file_path_adjacency_list[vertex1_file_path] = []

    def get_edges_for_vertex(self, vertex) -> list[DependencyGraphEdge]:
        return self._adjacency_list[vertex]

    def get_vertices(self) -> list[AstStatement]:
        return list(self._adjacency_list.keys())

    @property
    def degrees(self) -> int:
        return len(self.file_path_adjacency_list)

    def __str__(self):
        output = ""
        for vertex, edges in self._adjacency_list.items():
            output += f"{vertex.unparse_stmt}\n"
            for edge in edges:
                output += f"{vertex} -> {edge}\n"

        return output

    def topological_sort(self) -> list[tuple[int, str, str]]:
        visited = set()
        stack: list[tuple[int, str, str]] = []

        def dfs(vertex: AstStatement, is_root=False):
            visited.add(vertex)
            for edge in self._adjacency_list[vertex]:
                if edge.vertex2 not in visited:
                    dfs(edge.vertex2)
            vertex_tuple = vertex.unparse_tuple
            if vertex_tuple not in stack:
                if is_root:
                    ## we want the root to be last in the file so we change the statement index to 1e6
                    ## TODO: HACKY
                    stack.append(
                        (int(1e6) + vertex_tuple[0], vertex_tuple[1], vertex_tuple[2])
                    )
                elif (
                    isinstance(vertex.stmt, ast.If)
                    and ast.unparse(vertex.stmt.test) == "__name__ == '__main__'"
                ):
                    ## we want the name-main to be last in the file so we change the statement index to 1e8
                    stack.append(
                        (int(1e8) + vertex_tuple[0], vertex_tuple[1], vertex_tuple[2])
                    )
                else:
                    stack.append(vertex_tuple)

        for vertex in self.get_vertices():
            if vertex not in visited:
                dfs(vertex, True)

        return stack

    def topological_file_sort(self) -> list[str]:
        visited = set()
        file_order: list[str] = []

        def dfs(file_path: str):
            visited.add(file_path)
            if file_path in self.file_path_adjacency_list:
                for edge in self.file_path_adjacency_list[file_path]:
                    if edge not in visited:
                        dfs(edge)
            file_order.append(file_path)

        for file_path in self.file_path_adjacency_list.keys():
            if file_path not in visited:
                dfs(file_path)

        return file_order

    @staticmethod
    def partion_by_files(
        topological_sorted_stack: list[tuple[int, str, str]]
    ) -> dict[str, list]:
        files = defaultdict(list)
        for idx, stmt, file_path in topological_sorted_stack:
            files[file_path].append((idx, stmt))
        return files

    def unparse(
        self,
        unparse_type: DependencySliceUnparseEnum = DependencySliceUnparseEnum.PATH_COMMENT,
    ) -> str:
        topological_sorted_stack = self.topological_sort()
        topological_sorted_stack_partitioned = self.partion_by_files(
            topological_sorted_stack
        )

        output = ""

        file_order = self.topological_file_sort()

        if len(self._adjacency_list) == 0 and len(self.file_path_adjacency_list) == 0:
            if unparse_type == DependencySliceUnparseEnum.MARKDOWN_FILES:
                output += f"```python\n"
            file_path_display = self._inputstmts[0].file_path.removeprefix(
                self._repo_path
            )[1:]
            output += f"## {file_path_display}\n"
            for function_obj in self._inputstmts:
                output += f"{function_obj.unparse_stmt}\n\n"
            if unparse_type == DependencySliceUnparseEnum.MARKDOWN_FILES:
                output += f"```\n\n\n"
            else:
                output += f"\n\n\n"
            return output

        assert len(file_order) > 0, f"{self._adjacency_list=}\n{self._inputstmts=}"

        for file_path in file_order:
            file_path_display = file_path.removeprefix(self._repo_path)[1:]
            statements = topological_sorted_stack_partitioned[file_path]
            if unparse_type == DependencySliceUnparseEnum.MARKDOWN_FILES:
                output += f"```python\n"
            output += f"## {file_path_display}\n"
            sorted_statements = sorted(statements, key=lambda x: x[0])
            for _, unparsed_stmt in sorted_statements:
                output += unparsed_stmt + "\n\n"
            if unparse_type == DependencySliceUnparseEnum.MARKDOWN_FILES:
                output += f"```\n\n\n"
            else:
                output += f"\n\n\n"

        return output

    def unparse_by_file(
        self,
    ) -> dict[str, str]:
        topological_sorted_stack = self.topological_sort()
        topological_sorted_stack_partitioned = self.partion_by_files(
            topological_sorted_stack
        )

        output = ""

        file_order = self.topological_file_sort()

        if len(self._adjacency_list) == 0 and len(self.file_path_adjacency_list) == 0:
            output = ""
            file_path_display = self._inputstmts[0].file_path.removeprefix(
                self._repo_path
            )[1:]
            for function_obj in self._inputstmts:
                output += f"{function_obj.unparse_stmt}\n\n"
            return {file_path_display: output}

        assert len(file_order) > 0, f"{self._adjacency_list=}\n{self._inputstmts=}"

        file_output = {}
        for file_path in file_order:
            file_path_display = file_path.removeprefix(self._repo_path)[1:]
            statements = topological_sorted_stack_partitioned[file_path]
            output = ""
            for _, unparsed_stmt in statements:
                output += unparsed_stmt + "\n\n"
            file_output[file_path_display] = output

        return file_output
