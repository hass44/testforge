import os
from pathlib import Path
from typing import Any


def file_to_import_path(file_path: str, project_root: str | None = None) -> str:
    root = Path(project_root) if project_root else Path.cwd()
    rel = Path(file_path).resolve().relative_to(root.resolve())
    return str(rel.with_suffix("")).replace(os.sep, ".")


def build_context(
    metadata: dict[str, Any],
    mode: str = "full_source",
    import_path: str | None = None,
) -> str:
    if mode == "full_source":
        return _build_lean(metadata, import_path)
    elif mode == "retrieved_chunks":
        raise NotImplementedError(
            "Rich context for RAG/chunked mode — implement when retrieval is added"
        )
    else:
        raise ValueError(f"Unknown context mode: {mode!r}")


def _build_lean(metadata: dict[str, Any], import_path: str | None = None) -> str:
    lines: list[str] = []
    lines.append("# Test targets")
    lines.append("Write tests for every item below. Full source code follows separately.\n")

    if import_path:
        lines.append(f"Import the module under test as: `from {import_path} import ...`\n")

    for func in metadata.get("functions", []):
        lines.append(_format_target(func, class_name=None))

    for cls in metadata.get("classes", []):
        lines.append(f"class {cls['name']}:")
        for method in cls.get("methods", []):
            lines.append(_format_target(method, class_name=cls["name"]))
        lines.append("")

    return "\n".join(lines)


def _format_target(func: dict[str, Any], class_name: str | None) -> str:
    prefix = "  " if class_name else ""
    async_marker = "async " if func.get("is_async") else ""
    raises = func.get("raises", [])
    raises_note = f"  [raises: {', '.join(raises)}]" if raises else ""
    return f"{prefix}- {async_marker}{func['name']}(){raises_note}"
