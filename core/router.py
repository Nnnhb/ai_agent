
"""
UIE Router

The Decision Engine is the authoritative routing system
for UIE.

The old router independently selected specialists through
LLM handoffs. That created two competing routing systems:

    User
      ↓
    Router
      ↓
    Specialist

and:

    User
      ↓
    Decision Engine
      ↓
    Dispatcher
      ↓
    Specialist

UIE now uses the second architecture.

This module is temporarily kept as a compatibility layer
so existing imports do not break while the architecture
is being cleaned up.
"""

from core.decision import decision_agent


# ------------------------------------------------------------
# COMPATIBILITY ALIAS
# ------------------------------------------------------------
#
# Existing files may still import:
#
#     from core.router import router_agent
#
# Instead of maintaining a second routing system, the
# router now points to the authoritative Decision Engine.
#
# This means there is only one routing intelligence.
#

router_agent = decision_agent