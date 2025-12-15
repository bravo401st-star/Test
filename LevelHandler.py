import math
import EventSystem

# ===== EXPERIENCE FORMULA CONSTANTS =====
EXP_BASE_MULTIPLIER = 5  # Base amount of experience needed at level 1
EXP_GROWTH_RATE = 0.3    # Exponential growth rate per level

class LevelHandler():
    def __init__(self):
        self.heldExperience = 0
        self.level = 1
        self.neededExperience = getNeededExp(self.level)
        self.e_OnLevelUp = EventSystem.Event()


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
        self.e_OnLevelUp.Trigger()
        
    
    def __str__(self):
        return str(self.level)


def getNeededExp(level: int):
    return math.floor(EXP_BASE_MULTIPLIER * math.exp(EXP_GROWTH_RATE * (level - 1)))
    