class RPGStats:
    def __init__(self):
        self.strength = 1
        self.dexterity = 1
        self.intelligence = 1
        self.wisdom = 1
        self.charisma = 1
        self.constitution = 1

    def SetStrength(self, strength: int):
        self.strength = strength
        return self
    
    def SetDexterity(self, dexterity: int):
        self.dexterity = dexterity
        return self
    
    def SetIntelligence(self, intelligence: int):
        self.intelligence = intelligence
        return self
    
    def SetWisdom(self, wisdom: int):
        self.wisdom = wisdom
        return self
    
    def SetCharisma(self, charisma: int):
        self.charisma = charisma
        return self
    
    def SetConstitution(self, constitution: int):
        self.constitution = constitution
        return self
