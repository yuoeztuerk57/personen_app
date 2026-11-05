class Person:
    def __init__(self, name, alter, adresse):
        self.name = name
        self.alter = alter
        self.adresse = adresse

    def to_dict(self):
        return {
            "name": self.name,
            "alter": self.alter,
            "adresse": self.adresse
        }