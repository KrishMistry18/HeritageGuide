import os
from typing import Optional

from supabase import Client, create_client


def _create(url: str, key: str) -> Optional[Client]:
    if not url or not key:
        return None
    return create_client(url, key)


def get_supabase_anon_client() -> Optional[Client]:
    return _create(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_ANON_KEY", ""),
    )


def get_supabase_service_client() -> Optional[Client]:
    return _create(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )
