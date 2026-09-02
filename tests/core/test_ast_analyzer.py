"""测试 AST 依赖分析器：各种代码模式的 defs/refs 提取。"""

from __future__ import annotations

import pytest

from backend.core.ast_analyzer import AnalysisError, analyze_cell


def analyze(code: str) -> tuple[set[str], set[str]]:
    return analyze_cell(code)


def test_empty_code():
    assert analyze("") == (set(), set())
    assert analyze("   \n  ") == (set(), set())


def test_simple_assignment():
    defs, refs = analyze("x = 1")
    assert defs == {"x"}
    assert refs == set()


def test_use_external_variable():
    defs, refs = analyze("y = x + 1")
    assert defs == {"y"}
    assert refs == {"x"}


def test_multiple_assignment():
    defs, refs = analyze("a, b = 1, 2")
    assert defs == {"a", "b"}
    assert refs == set()


def test_function_definition():
    defs, refs = analyze("def foo():\n    return 1")
    assert defs == {"foo"}
    assert refs == set()


def test_function_with_external_ref():
    defs, refs = analyze("def foo():\n    return x + 1")
    assert defs == {"foo"}
    assert refs == {"x"}


def test_function_internal_local_not_counted():
    defs, refs = analyze("def foo():\n    z = 1\n    return z")
    assert defs == {"foo"}
    assert refs == set()


def test_class_definition():
    defs, refs = analyze("class Foo:\n    pass")
    assert defs == {"Foo"}
    assert refs == set()


def test_class_with_base():
    defs, refs = analyze("class Foo(Base):\n    pass")
    assert defs == {"Foo"}
    assert refs == {"Base"}


def test_import():
    defs, refs = analyze("import os")
    assert defs == {"os"}
    assert refs == set()


def test_import_as():
    defs, refs = analyze("import os.path as p")
    assert defs == {"p"}
    assert refs == set()


def test_import_dotted():
    defs, refs = analyze("import os.path")
    assert defs == {"os"}
    assert refs == set()


def test_from_import():
    defs, refs = analyze("from os import path")
    assert defs == {"path"}
    assert refs == set()


def test_from_import_as():
    defs, refs = analyze("from os import path as p")
    assert defs == {"p"}
    assert refs == set()


def test_for_loop():
    defs, refs = analyze("for i in range(10):\n    pass")
    assert defs == {"i"}
    assert refs == set()


def test_for_unpacking():
    defs, refs = analyze("for i, (a, b) in items:\n    pass")
    assert defs == {"i", "a", "b"}
    assert refs == {"items"}


def test_aug_assign():
    defs, refs = analyze("x += 1")
    assert defs == {"x"}
    assert refs == {"x"}


def test_walrus():
    defs, refs = analyze("(x := 1)")
    assert defs == {"x"}
    assert refs == set()


def test_comprehension_local():
    defs, refs = analyze("result = [x for x in range(10)]")
    assert defs == {"result"}
    assert refs == set()


def test_with_statement():
    defs, refs = analyze('with open("f") as f:\n    pass')
    assert defs == {"f"}
    assert refs == set()


def test_self_define_and_use():
    defs, refs = analyze("x = 1\ny = x + 1")
    assert defs == {"x", "y"}
    assert refs == {"x"}


def test_syntax_error():
    with pytest.raises(AnalysisError):
        analyze("def foo(:")