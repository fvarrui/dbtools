from dataclasses import dataclass, asdict

@dataclass
class Column:

    name: str
    type: str
    comment: str

    def __init__(self, metadata: any):
        self.name = metadata.name
        self.type = str(metadata.type)
        self.comment = metadata.comment

    def __eq__(self, value):
        return self.name == value.name and self.type == value.type

    def __dict__(self):
        return asdict(self)