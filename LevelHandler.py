import math

class LevelHandler():
    def __init__(self):
        self.heldExperience = 0
        self.level = 1
        self.neededExperience = getNeededExp(self.level)
        pass

    def GrantExperience(self, amount: int):
        if type(amount) != int:
            return
        
        self.SetExperience(self.heldExperience + amount)
    

    def SetExperience(self, amount: int):
        if type(amount) != int:
            return
        
        self.heldExperience = amount
        if self.heldExperience >= self.neededExperience:
            self.SetExperience(self.heldExperience - self.neededExperience)
            self.LevelUp()

    
    def LevelUp(self):
        self.level += 1
        self.neededExperience = getNeededExp(self.level)
        
    
    def __str__(self):
        return str(self.level)


def getNeededExp(level: int):
    return math.floor(5 * math.exp(0.2 * (level - 1)))
    