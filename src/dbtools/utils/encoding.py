import base64
import datetime
from decimal import Decimal

def serializable_dict(row : dict) -> dict:
    for k, v in row.items():
        if isinstance(v, bytes):
            row[k] = base64.b64encode(v).decode("utf-8")
        elif isinstance(v, Decimal):
            row[k] = float(v)
        elif isinstance(v, datetime.datetime):
            row[k] = v.isoformat()
    return row