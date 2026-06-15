import os

import pytest

os.environ.setdefault("SILICONFLOW_API_KEY", "sk-test-bootstrap")

from src.models.embed import OtherEmbedding


def _embedding(api_key: str = "SILICONFLOW_API_KEY") -> OtherEmbedding:
    return OtherEmbedding(
        model="Pro/BAAI/bge-m3",
        base_url="https://api.siliconflow.cn/v1/embeddings",
        api_key=api_key,
    )


def test_other_embedding_rejects_inline_comment_api_key(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "# 推荐使用硅基流动免费服务")

    with pytest.raises(ValueError, match="inline comment"):
        _embedding().build_headers()


def test_other_embedding_rejects_missing_env_api_key(monkeypatch):
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    with pytest.raises(ValueError, match="SILICONFLOW_API_KEY"):
        _embedding().build_headers()


def test_other_embedding_rejects_placeholder_api_key(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "replace-with-siliconflow-api-key")

    with pytest.raises(ValueError, match="placeholder"):
        _embedding().build_headers()


def test_other_embedding_rejects_non_ascii_api_key(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "中文密钥")

    with pytest.raises(ValueError, match="only support ASCII"):
        _embedding().build_headers()


def test_other_embedding_omits_authorization_for_no_api_key():
    assert _embedding(api_key="no_api_key").build_headers() == {"Content-Type": "application/json"}


def test_other_embedding_adds_authorization_for_valid_api_key(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "sk-test")

    headers = _embedding().build_headers()

    assert headers["Authorization"] == "Bearer sk-test"
    assert headers["Content-Type"] == "application/json"
