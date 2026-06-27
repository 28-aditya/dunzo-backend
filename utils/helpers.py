from datetime import datetime
import uuid

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