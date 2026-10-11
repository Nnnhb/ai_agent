from pathlib import Path
import subprocess
import sys

from agents import function_tool


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _safe_python_path(filename: str):
    """
    Resolve a Python file while ensuring it remains
    inside the UIE project.
    """

    file_path = (PROJECT_ROOT / filename).resolve()

    if PROJECT_ROOT not in file_path.parents:
        return None, "Access denied: file is outside the UIE project."

    if file_path.suffix != ".py":
        return None, "Only Python files can be accessed."

    return file_path, None


@function_tool
def run_python_file(filename: str) -> str:
    """
    Run a Python file located inside the UIE project.
    """

    file_path, error = _safe_python_path(filename)

    if error:
        return error

    if not file_path.exists():
        return f"File not found: `{filename}`"

    try:
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=PROJECT_ROOT,
        )

        output = result.stdout.strip()
        errors = result.stderr.strip()

        if result.returncode == 0:
            return (
                "Execution successful:\n\n"
                f"{output}"
            )

        return (
            f"Execution failed with exit code "
            f"{result.returncode}.\n\n"
            f"Output:\n{output}\n\n"
            f"Errors:\n{errors}"
        )

    except subprocess.TimeoutExpired:
        return (
            "Execution stopped: Python file exceeded "
            "the 30-second timeout."
        )

    except Exception as error:
        return f"Execution error: {error}"


@function_tool
def edit_python_file(
    filename: str,
    new_content: str,
) -> str:
    """
    Replace the complete contents of a Python file
    inside the UIE project.

    Only Python files inside the project are allowed.
    """

    file_path, error = _safe_python_path(filename)

    if error:
        return error

    if not file_path.exists():
        return f"File not found: `{filename}`"

    try:
        file_path.write_text(
            new_content,
            encoding="utf-8",
        )

        return f"Successfully updated `{filename}`."

    except Exception as error:
        return f"Failed to update `{filename}`: {error}"
