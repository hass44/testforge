import os
import re
from typing import Any

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from testforge.analysis.prompt_context import build_context, file_to_import_path

load_dotenv()

_SYSTEM_PROMPT = (
    "You are an expert Python developer specializing in writing unit tests. "
    "Your task is to write a pytest suite for the provided code.\n"
    "CRITICAL: Output ONLY valid, executable Python code. "
    "Do NOT wrap your code in markdown code blocks like ```python. "
    "Do NOT write any intro text, outro text, or explanations."
)


def generate_pytest_suite(
    source_code: str,
    metadata: dict[str, Any],
    file_path: str | None = None,
    model: str | None = None,
) -> str:
    model = model or os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-30B-A3B-Instruct")
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN not set — add it to your .env file")

    client = InferenceClient(token=token)

    import_path = file_to_import_path(file_path) if file_path else None
    test_targets = build_context(metadata, mode="full_source", import_path=import_path)

    user_prompt = (
        f"{test_targets}\n\n"
        f"# Source code under test\n"
        f"```python\n{source_code}\n```\n\n"
        f"Write a comprehensive pytest suite covering all targets above, "
        f"including edge cases and error paths."
    )

    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=4096,
        )
    except HfHubHTTPError as e:
        raise RuntimeError(
            f"HuggingFace API error for model {model!r}. "
            f"The model may not be available on the free tier. "
            f"Try a different MODEL_NAME in .env.\n"
            f"Original error: {e}"
        ) from e

    raw = response.choices[0].message.content
    return _strip_markdown_fences(raw)


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    return text.strip()
