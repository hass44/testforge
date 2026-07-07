import ast
from typing import Any


class SourceVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self._current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef):
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": [],
            "lineno": node.lineno,
        }
        self.classes.append(class_info)

        prev_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = prev_class

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        func_info = {
            "name": node.name,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "args": _extract_args(node.args),
            "returns": _unparse_annotation(node.returns),
            "raises": _extract_raises(node),
            "docstring": ast.get_docstring(node) or "",
            "lineno": node.lineno,
        }

        if self._current_class:
            for cls in self.classes:
                if cls["name"] == self._current_class:
                    cls["methods"].append(func_info)
                    break
        else:
            self.functions.append(func_info)

        self.generic_visit(node)

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function


def _unparse_annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    return ast.unparse(node)


def _extract_args(args: ast.arguments) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    num_pos_only = len(args.posonlyargs)
    num_regular = len(args.args)
    num_defaults = len(args.defaults)
    defaults_offset = num_pos_only + num_regular - num_defaults

    for i, arg in enumerate(args.posonlyargs + args.args):
        default_index = i - defaults_offset
        result.append(
            {
                "name": arg.arg,
                "annotation": _unparse_annotation(arg.annotation),
                "default": (
                    ast.unparse(args.defaults[default_index])
                    if default_index >= 0
                    else None
                ),
                "kind": "positional_only" if i < num_pos_only else "positional",
            }
        )

    if args.vararg:
        result.append(
            {
                "name": args.vararg.arg,
                "annotation": _unparse_annotation(args.vararg.annotation),
                "default": None,
                "kind": "var_positional",
            }
        )

    for i, arg in enumerate(args.kwonlyargs):
        default_node = args.kw_defaults[i]
        result.append(
            {
                "name": arg.arg,
                "annotation": _unparse_annotation(arg.annotation),
                "default": ast.unparse(default_node) if default_node else None,
                "kind": "keyword_only",
            }
        )

    if args.kwarg:
        result.append(
            {
                "name": args.kwarg.arg,
                "annotation": _unparse_annotation(args.kwarg.annotation),
                "default": None,
                "kind": "var_keyword",
            }
        )

    return result


def _extract_raises(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    raises = []
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            if isinstance(child.exc, ast.Call):
                raises.append(ast.unparse(child.exc.func))
            elif isinstance(child.exc, ast.Name):
                raises.append(child.exc.id)
    return sorted(set(raises))


def analyze_code(source_code: str) -> dict[str, Any]:
    tree = ast.parse(source_code)
    visitor = SourceVisitor()
    visitor.visit(tree)
    return {
        "classes": visitor.classes,
        "functions": visitor.functions,
    }


def analyze_file(file_path: str) -> dict[str, Any]:
    with open(file_path, encoding="utf-8") as f:
        source_code = f.read()
    return analyze_code(source_code)
