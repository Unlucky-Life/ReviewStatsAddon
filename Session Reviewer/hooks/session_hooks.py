from aqt import mw, gui_hooks
import time
from ..utility import format_timestamp, format_duration, log_session

# Session state kept inside this module
session_active = False
session_start_ts = None


def collect_stats():
    """Collect review statistics from the current session.

    Queries Anki's revlog for entries after `session_start_ts` and
    aggregates counts for each ease rating. Returns a dict with counts,
    timestamps and total reviews.
    """
    global session_start_ts
    col = mw.col

    cards = col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id > ?",
        session_start_ts,
    ) or 0

    counts = col.db.first(
        """
        SELECT
            SUM(CASE WHEN ease=1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN ease=2 THEN 1 ELSE 0 END),
            SUM(CASE WHEN ease=3 THEN 1 ELSE 0 END),
            SUM(CASE WHEN ease=4 THEN 1 ELSE 0 END)
        FROM revlog WHERE id > ?
        """,
        session_start_ts,
    )

    now = int(time.time() * 1000)
    duration = now - session_start_ts

    total_reviews = sum(counts) if counts else 0

    return {
        "cards": cards,
        "again": counts[0] or 0,
        "hard": counts[1] or 0,
        "good": counts[2] or 0,
        "easy": counts[3] or 0,
        "time_start": session_start_ts,
        "time_end": now,
        "duration": duration,
        "total_reviews": total_reviews,
    }


def on_state_change(new_state, old_state):
    """Respond to Anki UI state transitions to start/end a review session."""
    global session_active, session_start_ts

    if new_state == "review":
        session_active = True
        session_start_ts = int(time.time() * 1000)

    if old_state == "review" and new_state != "review":
        on_reviewer_end()


gui_hooks.state_did_change.append(on_state_change)


def on_reviewer_end():
    """Finalize the review session: collect stats, show dialog and persist log."""
    global session_active, session_start_ts

    if not session_active or not session_start_ts:
        return

    stats = collect_stats()

    # Import here to avoid a package import cycle at module import time
    from ..GUI.stats_dialog import StatsDialog

    dlg = StatsDialog(stats, parent=mw)
    dlg.exec()

    # persist
    log_session(stats)

    session_active = False
    session_start_ts = None


gui_hooks.reviewer_will_end.append(on_reviewer_end)
