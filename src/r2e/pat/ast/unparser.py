import ast


def unparse_ast_stmt_with_comments(file_content: str, stmt: ast.stmt) -> str:
    """
    Unparse an AST statement with comments.
    """

    file_content_lines = file_content.split("\n")
    stmt_start_lineno = stmt.lineno - 1
    stmt_start_col_offset = stmt.col_offset
    # TODO : Fix the type ignore, not sure why this is optional
    stmt_end_lineno = stmt.end_lineno - 1  # type: ignore
    stmt_end_col_offset = stmt.end_col_offset  # type: ignore

    stmt_lines = file_content_lines[stmt_start_lineno : stmt_end_lineno + 1]

    stmt_lines[0] = stmt_lines[0][stmt_start_col_offset:]
    stmt_lines[-1] = stmt_lines[-1][:stmt_end_col_offset]

    return "\n".join(stmt_lines)
