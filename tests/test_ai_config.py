"""
Unit tests for AI Configuration & Secret Security:
API masking, placeholder detection, and fallback handling.
"""

import pytest
import config
from src.api.featherless_client import FeatherlessClient


def test_api_key_placeholder_detection():
    """Verify that placeholder keys are flagged as unconfigured."""
    c1 = FeatherlessClient(api_key="")
    assert not c1.is_configured()

    c2 = FeatherlessClient(api_key="your_featherless_api_key_here")
    assert not c2.is_configured()

    c3 = FeatherlessClient(api_key="placeholder_12345")
    assert not c3.is_configured()

    c4 = FeatherlessClient(api_key="sk-valid-key-abcdef123456789")
    assert c4.is_configured()


def test_fallback_reply_without_key():
    """Client must return institutional fallback without crashing when key is absent."""
    client = FeatherlessClient(api_key="")
    res = client.chat_completion(
        messages=[{"role": "user", "content": "Explain the Sharpe ratio"}]
    )
    assert not res["configured"]
    assert "Sharpe" in res["content"]
    assert len(res["content"]) > 50


def test_secret_sanitization_in_errors():
    """Verify that any exception string redacts the raw API key."""
    fake_secret = "secret-token-abcdef-987654321"
    client = FeatherlessClient(api_key=fake_secret, base_url="http://invalid.url.local.test")
    test_res = client.test_connection()

    assert not test_res["success"]
    assert fake_secret not in test_res["message"]
