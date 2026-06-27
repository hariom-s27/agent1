"""A trivial 'smoke test' for Phase 0.

Its only job: prove that pytest runs and the project imports.
We replace this with real tests starting in Phase 2.
"""


def test_toolchain_works():
    # If pytest runs this and it passes, your setup is correct.
    assert 1 + 1 == 2


def test_package_imports():
    import sidekick  # noqa: F401  (just checking the package imports)
