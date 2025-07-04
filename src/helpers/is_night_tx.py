from datetime import datetime, timezone

def is_night_tx(unix_ts: int) -> bool:
    return 0 <= datetime.fromtimestamp(unix_ts, timezone.utc).hour < 4