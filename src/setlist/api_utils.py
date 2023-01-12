__all__ = ["generate_qstr"]


def generate_qstr(args: dict[str, str]) -> str:
    query = "?"

    for k, v in args.items():
        query += f"{k}={v}&"

    return query[:len(query)-1]
