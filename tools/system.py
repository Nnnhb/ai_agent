
"""
UIE System Tools

Controlled tools for reading basic information about the
machine running UIE.

Security principles:

- Do not execute arbitrary shell commands.
- Do not accept raw shell commands from the user.
- Do not delete or modify system files.
- Do not terminate processes.
- Do not expose unrestricted filesystem access.
- Return truthful information only.
- Keep system capabilities separate from coding tools.

These tools are intentionally read-only for now.

Future system capabilities should be added individually
with explicit security boundaries.
"""

import os
import platform
import shutil
from pathlib import Path

from agents import function_tool


# ============================================================
# PROJECT INFORMATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# SYSTEM INFORMATION
# ============================================================

@function_tool
def get_system_information() -> str:
    """
    Return basic information about the system running UIE.

    This tool is read-only.
    """

    try:
        system_name = platform.system()
        system_version = platform.version()
        architecture = platform.machine()
        processor = platform.processor()
        python_version = platform.python_version()

        return (
            "System Information\n"
            "==================\n"
            f"Operating system: {system_name}\n"
            f"OS version: {system_version}\n"
            f"Architecture: {architecture}\n"
            f"Processor: {processor or 'Unknown'}\n"
            f"Python version: {python_version}"
        )

    except Exception as error:
        return f"Could not read system information: {error}"


# ============================================================
# CPU INFORMATION
# ============================================================

@function_tool
def get_cpu_information() -> str:
    """
    Return basic CPU information.

    This is a read-only operation.
    """

    try:
        logical_cpus = os.cpu_count()

        return (
            "CPU Information\n"
            "===============\n"
            f"Logical CPU count: "
            f"{logical_cpus if logical_cpus else 'Unknown'}"
        )

    except Exception as error:
        return f"Could not read CPU information: {error}"


# ============================================================
# MEMORY INFORMATION
# ============================================================

@function_tool
def get_memory_information() -> str:
    """
    Return basic memory information when available.

    Uses platform-independent information where possible.
    """

    try:
        # macOS / Linux / Unix-like systems
        if hasattr(os, "sysconf"):

            page_size = os.sysconf("SC_PAGE_SIZE")
            physical_pages = os.sysconf("SC_PHYS_PAGES")

            total_memory = page_size * physical_pages

            total_gb = total_memory / (
                1024 ** 3
            )

            return (
                "Memory Information\n"
                "==================\n"
                f"Total physical memory: "
                f"{total_gb:.2f} GB"
            )

        return (
            "Memory information is not available "
            "on this platform."
        )

    except Exception as error:
        return f"Could not read memory information: {error}"


# ============================================================
# DISK INFORMATION
# ============================================================

@function_tool
def get_disk_information() -> str:
    """
    Return disk-space information for the UIE project drive.

    This tool is read-only.
    """

    try:
        usage = shutil.disk_usage(PROJECT_ROOT)

        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)

        return (
            "Disk Information\n"
            "================\n"
            f"Project location: {PROJECT_ROOT}\n"
            f"Total space: {total_gb:.2f} GB\n"
            f"Used space: {used_gb:.2f} GB\n"
            f"Free space: {free_gb:.2f} GB"
        )

    except Exception as error:
        return f"Could not read disk information: {error}"


# ============================================================
# PROJECT INFORMATION
# ============================================================

@function_tool
def get_uie_project_information() -> str:
    """
    Return basic information about the UIE project itself.

    This tool does not modify anything.
    """

    try:
        exists = PROJECT_ROOT.exists()

        if not exists:
            return "UIE project directory could not be found."

        directories = sorted(
            item.name
            for item in PROJECT_ROOT.iterdir()
            if item.is_dir()
            and item.name != ".venv"
            and item.name != "__pycache__"
        )

        files = sorted(
            item.name
            for item in PROJECT_ROOT.iterdir()
            if item.is_file()
        )

        output = [
            "UIE Project Information",
            "=======================",
            f"Project root: {PROJECT_ROOT}",
            "",
            "Top-level directories:",
        ]

        if directories:
            output.extend(
                f"- {directory}"
                for directory in directories
            )
        else:
            output.append("- None")

        output.append("")
        output.append("Top-level files:")

        if files:
            output.extend(
                f"- {file}"
                for file in files
            )
        else:
            output.append("- None")

        return "\n".join(output)

    except Exception as error:
        return (
            f"Could not inspect UIE project information: "
            f"{error}"
        )
