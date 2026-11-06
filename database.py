import logging
import os
from datetime import datetime, timezone
from functools import lru_cache

from supabase import Client, create_client

logger = logging.getLogger("vynora-whatsapp.database")


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create one server-side Supabase client using the secret API key."""
    url = os.getenv("SUPABASE_URL", "").strip()
    secret_key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not url or not secret_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be configured")
    return create_client(url, secret_key)


def save_whatsapp_user(phone_number: str) -> None:
    """Insert or refresh a WhatsApp user; safe to call on repeated messages."""
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "phone_number": phone_number,
        "role": "user",
        "last_seen_at": now,
        "updated_at": now,
    }
    client.table("users").upsert(row, on_conflict="phone_number").execute()
