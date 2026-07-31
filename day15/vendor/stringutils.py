"""A helper module deliberately kept outside any package/install path.

It is not meant to be imported directly with `import vendor.stringutils`
(there is no `__init__.py` here on purpose) — the point of this day is to
make `solution.py` put `vendor/` itself onto `sys.path` and then
`import stringutils` as a top-level module.
"""


def slugify(text: str) -> str:
    """Normalize a store name: strip, lowercase, spaces to dashes."""
    text = text.strip().lower()
    return "-".join(text.split())
