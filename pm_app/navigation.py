"""Simple navigation callback holder for UI modules to call back into main dashboard."""

_dashboard_cb = None


def set_dashboard_callback(cb):
    global _dashboard_cb
    _dashboard_cb = cb


def go_dashboard(role, full_name):
    if _dashboard_cb:
        return _dashboard_cb(role, full_name)
    raise RuntimeError("Dashboard callback not set")
