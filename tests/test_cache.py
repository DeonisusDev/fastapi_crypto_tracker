from app.services.cache import get_cached_price, set_cache
import time
from unittest.mock import patch

def test_set_and_get_cache():
    set_cache("bitcoin", 75000.0)
    result = get_cached_price("bitcoin")
    assert result == 75000.0


def test_cache_miss():
    result = get_cached_price("nonexistent_coin")
    assert result is None


def test_cache_expiration():
    set_cache("bitcoin", 75000.0)
    
    # Simulate time passing to expire the cache (assuming cache expiration is set to 60 seconds)
    with patch("app.services.cache.time.time", return_value=time.time() + 61):
        result = get_cached_price("bitcoin")
    
    assert result is None


def test_cache_overwrite():
    set_cache("ethereum", 3000.0)
    set_cache("ethereum", 3200.0)
    result = get_cached_price("ethereum")
    assert result == 3200.0