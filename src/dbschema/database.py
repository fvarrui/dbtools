from dataclasses import dataclass, asdict
from urllib.parse import urlparse

@dataclass
class Database:

    name : str = None
    server : str = None
    port : int = None

    def __init__(self, server: str, port: int, name: str):
        self.server = server
        self.port = port
        self.name = name

    def __init__(self, dburl: str):
        parsedurl = urlparse(dburl)
        self.server = parsedurl.hostname
        self.port = parsedurl.port
        self.name = parsedurl.path[1:]

    def __dict__(self):
        return asdict(self)

