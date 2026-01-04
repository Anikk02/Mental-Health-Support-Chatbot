"""
Helper utilities for safe ObjectId conversion and recursive document cleanup.
"""

from bson import ObjectId
from datetime import datetime, timezone
from typing import Any, Dict


def oid(id_str: str):
    """
    Convert string to ObjectId safely.
    Returns None if invalid.
    """
    try:
        return ObjectId(id_str)
    except Exception:
        return None


# -------------------------------------------------------
# Recursive converter (ObjectId → str, datetime → ISO)
# -------------------------------------------------------
def _convert(value: Any) -> Any:
    """Recursively convert MongoDB-specific types to JSON-safe values."""
    
    # ObjectId → string
    if isinstance(value, ObjectId):
        return str(value)

    # datetime → ISO
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc).isoformat()

    # List → convert each item
    if isinstance(value, list):
        return [_convert(item) for item in value]

    # Dict → convert nested keys
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}

    # other types untouched
    return value


# -------------------------------------------------------
# Public API
# -------------------------------------------------------
def to_str_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB document to JSON-safe format:
    - '_id' renamed to 'id'
    - recursive ObjectId → string
    - datetime → ISO 8601
    """
    if not doc:
        return doc

    new_doc = {}

    for k, v in doc.items():
        if k == "_id":
            new_doc["id"] = str(v)
        else:
            new_doc[k] = _convert(v)

    return new_doc
