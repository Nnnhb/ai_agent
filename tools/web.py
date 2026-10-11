
"""
UIE Web Tools

Web research is currently handled by the OpenAI Agents SDK's
WebSearchTool through the Research Specialist.

This module does not expose a fake web-search function.

Keeping this module allows the project structure to remain
stable while web capabilities are managed by the Research
Specialist.
"""

# Web search is intentionally not implemented here yet.
#
# The authoritative web-search capability currently lives in:
#
#     app/specialists/research.py
#
# through:
#
#     WebSearchTool()
#
# Do not create a placeholder function that claims to search
# the web without actually performing a search.
