"""
Pytest Configuration
====================

Configure *pytest* to use with *OpenColorIO* if available.
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser) -> None:  # noqa: ANN001
    """Add a *pytest* option for test requiring *OpenColorIO*."""

    parser.addoption(
        "--with_ocio",
        action="store_true",
        default=False,
        help="run tests that require the OpenColorIO library",
    )


def pytest_configure(config) -> None:  # noqa: ANN001
    """Configure *pytest* for *OpenColorIO*."""

    config.addinivalue_line(
        "markers", "with_ocio: mark test that require the OpenColorIO library"
    )


def pytest_collection_modifyitems(config, items) -> None:  # noqa: ANN001
    """Modify *pytest* collection for *OpenColorIO*."""

    if config.getoption("--with_ocio"):
        return

    skip_slow = pytest.mark.skip(reason="need --with_ocio option to run")
    for item in items:
        if "with_ocio" in item.keywords:
            item.add_marker(skip_slow)
