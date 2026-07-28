from datetime import datetime


def local_now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")