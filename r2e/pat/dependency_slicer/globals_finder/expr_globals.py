import ast


class ExprGlobalVariablesVisitor(ast.NodeVisitor):
    def visit(self, node) -> list[str]:
        if node is None:
            return []
        return super().visit(node)

    def visit_Expr(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_Constant(self, node) -> list[str]:
        return []

    def visit_Name(self, node) -> list[str]:
        return [node.id]

    def visit_Attribute(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_Call(self, node) -> list[str]:
        globals = self.visit(node.func)
        for arg in node.args:
            globals.extend(self.visit(arg))
        return globals

    def visit_List(self, node) -> list[str]:
        return self.visit_elements(node.elts)

    def visit_Tuple(self, node) -> list[str]:
        return self.visit_elements(node.elts)

    def visit_Set(self, node) -> list[str]:
        return self.visit_elements(node.elts)

    def visit_Dict(self, node) -> list[str]:
        globals: list[str] = []
        for key, value in zip(node.keys, node.values):
            if key:
                globals.extend(self.visit(key))
            globals.extend(self.visit(value))
        return globals

    def visit_Subscript(self, node) -> list[str]:
        globals = self.visit(node.value)
        globals.extend(self.visit(node.slice))
        return globals

    def visit_BinOp(self, node) -> list[str]:
        globals = self.visit(node.left)
        globals.extend(self.visit(node.right))
        return globals

    def visit_UnaryOp(self, node) -> list[str]:
        return self.visit(node.operand)

    def visit_Slice(self, node) -> list[str]:
        globals: list[str] = []
        if node.lower:
            globals.extend(self.visit(node.lower))
        if node.upper:
            globals.extend(self.visit(node.upper))
        if node.step:
            globals.extend(self.visit(node.step))
        return globals

    def visit_Lambda(self, node) -> list[str]:
        body_globals = self.visit(node.body)
        argument_names = {arg.arg for arg in node.args.args}
        return [var for var in body_globals if var not in argument_names]

    def visit_IfExp(self, node) -> list[str]:
        globals = self.visit(node.test)
        globals.extend(self.visit(node.body))
        globals.extend(self.visit(node.orelse))
        return globals

    def visit_ListComp(self, node) -> list[str]:
        return self.handle_comprehension(node.elt, node.generators)

    def visit_SetComp(self, node) -> list[str]:
        return self.handle_comprehension(node.elt, node.generators)

    def visit_GeneratorExp(self, node) -> list[str]:
        return self.handle_comprehension(node.elt, node.generators)

    def visit_DictComp(self, node) -> list[str]:
        globals = self.visit(node.key)
        globals.extend(self.visit(node.value))
        for generator in node.generators:
            globals.extend(self.visit(generator.iter))
            for if_condition in generator.ifs:
                globals.extend(self.visit(if_condition))

            non_global_targets = self.visit(generator.target)
            globals = [var for var in globals if var not in non_global_targets]
        return globals

    def visit_Await(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_Yield(self, node) -> list[str]:
        return self.visit(node.value) if node.value else []

    def visit_YieldFrom(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_Compare(self, node) -> list[str]:
        globals = self.visit(node.left)
        for comparator in node.comparators:
            globals.extend(self.visit(comparator))
        return globals

    def visit_BoolOp(self, node) -> list[str]:
        globals: list[str] = []
        for value in node.values:
            globals.extend(self.visit(value))
        return globals

    def visit_JoinedStr(self, node) -> list[str]:
        globals: list[str] = []
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                globals.extend(self.visit(value.value))
        return globals

    def visit_FormattedValue(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_Starred(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_NamedExpr(self, node) -> list[str]:
        return self.visit(node.value)

    def visit_elements(self, elements):
        globals: list[str] = []
        for element in elements:
            globals.extend(self.visit(element))
        return globals

    def handle_comprehension(self, elt, generators):
        globals = self.visit(elt)
        for generator in generators:
            globals.extend(self.visit(generator.iter))
            for if_condition in generator.ifs:
                globals.extend(self.visit(if_condition))

            non_global_targets = self.visit(generator.target)
            globals = [var for var in globals if var not in non_global_targets]
        return globals


def get_expr_globals(ast_node: ast.expr) -> list[str]:
    visitor = ExprGlobalVariablesVisitor()
    return visitor.visit(ast_node)
