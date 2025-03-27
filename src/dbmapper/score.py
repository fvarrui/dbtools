class Score:

    name: str
    ratio: float

    def __init__(self, name, ratio):
        self.name = name
        self.ratio = ratio

    def __compare__(self, other):
        return self.ratio - other.ratio
        