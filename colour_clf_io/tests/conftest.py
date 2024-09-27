import pytest  # noqa: D100


def pytest_addoption(parser):  # noqa: D103
    parser.addoption(
        "--with_ocio",
        action="store_true",
        default=False,
        help="run tests that require the OpenColorIO library",
    )


def pytest_configure(config):  # noqa: D103
    config.addinivalue_line(
        "markers", "with_ocio: mark test that require the OpenColorIO library"
    )


def pytest_collection_modifyitems(config, items):  # noqa: D103
    if config.getoption("--with_ocio"):
        return
    skip_slow = pytest.mark.skip(reason="need --with_ocio option to run")
    for item in items:
        if "with_ocio" in item.keywords:
            item.add_marker(skip_slow)
