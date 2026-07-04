from typing import Any, TypedDict


class AgentState(TypedDict):
    source_code: str
    metadata: dict[str, Any]
    import_path: str
    file_path: str
    project_root: str
    max_iterations: int
    coverage_target: float

    test_code: str
    test_result: dict[str, Any]
    iteration: int
    strategy: str
    history: list[dict[str, Any]]
    status: str
