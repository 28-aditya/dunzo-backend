from datetime import datetime, timezone
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_dict(obj) -> dict:
    result = {}

    for c in obj.__table__.columns:
        val = getattr(obj, c.name)

        if isinstance(val, datetime):
            result[c.name] = val.isoformat()

        elif isinstance(val, uuid.UUID):
            result[c.name] = str(val)

        else:
            result[c.name] = val

    return result


def to_uuid(val) -> uuid.UUID:
    return val if isinstance(val, uuid.UUID) else uuid.UUID(str(val))
