def __getattr__(name):
    if name == "Association":
        from .association import Association
        return Association
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Association"]
