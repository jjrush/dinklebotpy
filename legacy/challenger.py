class Challenger():
    def __init__(self, name, points):
        self.name = name
        self.points = points

    def changeName(self, name):
        self.name = name

    def name(self):
        return self.name

    def points(self):
        return self.points

    def addPoints(self, points):
        self.points = self.points + points

    def subtractPoints(self, points):
        self.points = self.points - points