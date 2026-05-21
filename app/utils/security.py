from __future__ import annotations

from urllib.parse import urljoin, urlparse

from flask import request


def is_safe_url(target: str | None) -> bool:
    if not target:
        return False

    reference_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in {"http", "https"} and reference_url.netloc == test_url.netloc


def get_safe_redirect_target(target: str | None) -> str | None:
    return target if is_safe_url(target) else None