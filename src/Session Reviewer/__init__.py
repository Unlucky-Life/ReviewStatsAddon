from aqt import mw, gui_hooks
from aqt.qt import *
"""Package bootstrap for ReviewStatsAddon.

This file keeps the package import surface small: importing the package
will import the utility helpers, GUI dialogs and register the session
hooks with Anki.
"""

# Import helpers, GUI and hooks so side-effects (hook registration) run.
from . import utility
from . import GUI
from .hooks import session_hooks

__all__ = ["utility", "GUI", "session_hooks"]

