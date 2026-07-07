"""Unit tests for the AST-based code analyzer."""

import textwrap

from testforge.analysis.analyzer import analyze_code


def test_extracts_function():
    code = textwrap.dedent("""\
        def greet(name: str) -> str:
            return f"Hello, {name}"
    """)
    result = analyze_code(code)
    assert len(result["functions"]) == 1
    fn = result["functions"][0]
    assert fn["name"] == "greet"
    assert fn["returns"] == "str"
    assert not fn["is_async"]


def test_extracts_async_function():
    code = textwrap.dedent("""\
        async def fetch(url: str) -> bytes:
            pass
    """)
    result = analyze_code(code)
    fn = result["functions"][0]
    assert fn["is_async"] is True


def test_extracts_class():
    code = textwrap.dedent("""\
        class Calculator:
            def add(self, a: int, b: int) -> int:
                return a + b
    """)
    result = analyze_code(code)
    assert len(result["classes"]) == 1
    cls = result["classes"][0]
    assert cls["name"] == "Calculator"
    assert len(cls["methods"]) == 1
    assert cls["methods"][0]["name"] == "add"


def test_extracts_raises():
    code = textwrap.dedent("""\
        def divide(a: int, b: int) -> float:
            if b == 0:
                raise ValueError("division by zero")
            return a / b
    """)
    result = analyze_code(code)
    fn = result["functions"][0]
    assert "ValueError" in fn["raises"]


def test_empty_file():
    result = analyze_code("")
    assert result["functions"] == []
    assert result["classes"] == []
