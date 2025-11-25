from aqt import mw
import os, time, math

# Paths for persistent files inside the add-on folder
LOG_FILE = os.path.join(mw.pm.addonFolder(), "reviewstats_log.txt")
XP_FILE = os.path.join(mw.pm.addonFolder(), "reviewxp.txt")


def load_xp():
    # Read stored XP from disk. If the file does not exist, return 0.
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return int(f.read().strip() or 0)
    return 0


def format_timestamp(ms):
    """Convert milliseconds since epoch to a readable timestamp string (YYYY-MM-DD HH:MM:SS)."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ms / 1000))


def format_duration(ms):
    """Convert milliseconds to a duration string in HH:MM:SS format."""
    seconds = int(ms / 1000)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def add_xp(amount):
    # Increase stored XP by `amount` and persist to disk. Returns new total XP.
    xp = load_xp() + amount
    with open(XP_FILE, "w") as f:
        f.write(str(xp))
    return xp


def xp_to_level(xp, base=100):
    """Convert total XP to a level and progress toward next level.

    Level formula: cumulative XP to reach level L is base * L*(L-1)/2.
    Returns (level, progress_into_level, xp_needed_for_this_level).
    """
    if xp < 0:
        xp = 0
    try:
        L = int((1 + math.sqrt(1 + 8 * xp / base)) // 2)
    except Exception:
        L = 1
    xp_prev = base * L * (L - 1) // 2
    xp_for_level = base * L
    progress = xp - xp_prev
    if progress < 0:
        progress = 0
    return L, progress, xp_for_level


def log_session(stats):
    """Append a session summary line to the persistent log file."""
    line = (
        f"{format_timestamp(stats['time_start'])},"
        f"{format_timestamp(stats['time_end'])},"
        f"{format_duration(stats['duration'])},"
        f"{stats['cards']},"
        f"{stats['again']},{stats['hard']},{stats['good']},{stats['easy']}\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


__all__ = [
    "LOG_FILE",
    "XP_FILE",
    "load_xp",
    "add_xp",
    "xp_to_level",
    "format_timestamp",
    "format_duration",
    "log_session",
]
