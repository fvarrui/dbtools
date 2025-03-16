
class ForeignKey:

    def __init__(self, name : str, referencing_column : str, referenced_table : str, referenced_column : str):
        self.name = name
        self.referencing_column = referencing_column
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column

    def __str__(self):
        return f"{self.referencing_column} -> {self.referenced_table}.{self.referenced_column} ({self.name})"
    
    def __repr__(self):
        return self.__str__()
