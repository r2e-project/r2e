import ast
import os


class ModuleExplorer:
    @staticmethod
    def get_member_names(module_path: str) -> list[str]:
        """Get the names of all members (functions, classes, variables) defined in a module.

        Args:
            module_path (str): The path to the module file.

        Returns:
            list[str]: A list of member names.
        """
        with open(module_path, "r") as file:
            tree = ast.parse(file.read())

        member_names = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                member_names.append(node.name)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    member = alias.name if alias.asname is None else alias.asname
                    if member == "*":
                        continue
                    member_names.append(
                        member.split(".")[0]
                    )  # only the first part of the member
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        member_names.append(target.id)
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    member_names.append(node.target.id)

        return member_names

    @staticmethod
    def get_package_name(module_path: str) -> str:
        """Get the name of the package containing the module.

        Args:
            module_path (str): The path to the module file.

        Returns:
            str: The (dotted) package name.
        """
        parts = []
        current_dir = os.path.dirname(module_path)

        while os.path.exists(os.path.join(current_dir, "__init__.py")):
            parts.append(os.path.basename(current_dir))
            current_dir = os.path.dirname(current_dir)

        if parts:
            return ".".join(reversed(parts))
        else:
            ## if the module is at the root of the package
            return os.path.basename(current_dir)

    @staticmethod
    def get_package_root(module_path: str) -> str:
        """Get the root directory of the package containing the module.

        Args:
            module_path (str): The path to the module file.

        Returns:
            str: The package root directory.
        """
        current_dir = os.path.dirname(module_path)

        while os.path.exists(os.path.join(current_dir, "__init__.py")):
            current_dir = os.path.dirname(current_dir)

        return current_dir

    @staticmethod
    def get_dependencies(path_to_module: str) -> dict[str, object]:
        """Get the dependencies of a module.

        Args:
            path_to_module (str): The path to the module file.

        Returns:
            dict[str, object]: A map `{name: imported_module}`
                where `name` is the name of an imported module
                and `imported_module` is the module object.
        """
        with open(path_to_module, "r") as file:
            module_code = file.read()

        tree = ast.parse(module_code)
        # find all import statements
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

        dependencies = {}
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    module_name = alias.name
                    referred_name = alias.asname if alias.asname else alias.name

                    # try to import the module and get the object
                    try:
                        imported_module = __import__(module_name)
                        dependencies[referred_name] = imported_module
                    except ModuleNotFoundError:
                        pass
                    except AttributeError:
                        pass

            elif isinstance(imp, ast.ImportFrom):
                module_name = imp.module

                assert module_name is not None, "Module name None (ImportFrom)?"

                if imp.level > 0:
                    package_name = ModuleExplorer.get_package_name(path_to_module)
                    module_name = ".".join([package_name, module_name])

                # try to import the module and get the object
                try:
                    imported_module = __import__(
                        module_name, fromlist=[alias.name for alias in imp.names]
                    )

                    for alias in imp.names:
                        referred_name = alias.asname if alias.asname else alias.name
                        dependencies[referred_name] = getattr(
                            imported_module, alias.name
                        )

                except ModuleNotFoundError:
                    pass
                except AttributeError:
                    pass

        return dependencies
