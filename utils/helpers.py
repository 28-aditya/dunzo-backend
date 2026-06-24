def to_dict(obj) -> dict:
    result = {}
    for c in obj.__table__.columns:
        val = getattr(obj, c.name)
        if hasattr(val, "isoformat"):  # datetime
            result[c.name] = val.isoformat()
        elif hasattr(val, "hex"):      # UUID
            result[c.name] = str(val)
        else:
            result[c.name] = val
    return result