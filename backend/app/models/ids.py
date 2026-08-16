import uuid


def new_id(prefix: str) -> str:
    """Genera un id legible tipo `ana_3f9c1a2b4d5e`."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
