"""Role gates used by admin (and other privileged) routes."""

from ..core.security_deps import require_role, get_current_role, get_current_user

__all__ = ["require_role", "get_current_role", "get_current_user"]
