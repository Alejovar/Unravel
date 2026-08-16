import uuid


def new_id(prefix: str) -> str:
    """Generates a readable id such as `ana_3f9c1a2b4d5e`."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
