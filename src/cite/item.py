import hashlib
from pathlib import Path


class Item:
    def __init__(self, path: Path):
        self.path = path
        self.id = self._hashify()

    def __eq__(self, other: "Item") -> bool:
        if not isinstance(other, Item):
            return False
        return self.id == other.id
    
    def __repr__(self) -> str:
        return self.id

    def _hashify(self) -> str:
        return hashlib.md5(b"{Path.read_text(self.path)}").hexdigest()
