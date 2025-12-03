from pathlib import Path
from tempfile import mkstemp
from cite.item import Item


class Db:
    """
    This class is responsible for interacting with the filesystem.
    """

    _store = Path.home() / ".local/share/cite"

    def __init__(self):
        if not Db._store.exists():
            Db._store.mkdir()

        self.items = self._iterdb()

    def _iterdb(self):
        """Generator that lazily instantiates Item objects."""
        for path in Db._store.iterdir():
            yield Item(path)

    def create(self, id: str, content: str) -> bool:
        _, tmp = mkstemp()
        tmp = Path(tmp)
        tmp.write_text(content)
        tmp = Item(tmp)

        if tmp in self.items:
            return False

        new = Db._store / f"{id}.bib"
        new.write_text(content)
        self.items = self._iterdb()
        return True
