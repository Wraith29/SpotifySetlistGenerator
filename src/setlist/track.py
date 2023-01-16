__all__ = ["Track"]


class Track:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    def __repr__(self) -> str:
        return f"Track(Name: {self.name})"
