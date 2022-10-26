"""Utils for naming convention."""


def normalize_plural(data):
    """Normalize data to ensure having list[any] to ease data processing.

    Frequently Salt provides:
    - a any (any type of data) if there is only one result
    - a list[any] if there are many
    """
    return data if isinstance(data, list) else [data]
