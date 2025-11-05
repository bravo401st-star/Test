import GameCore as gc

class Item():
    def __init__(self, name, rarity):
        self.name = name
        self.rarity = rarity
        pass
    

    def GetDesc(self):
        return self.name


class UseableItem(Item):
    def __init__(self, name, rarity, useCost):
        super().__init__(name, rarity)
        self.useCost = useCost


    def GetDesc(self):
        return super().GetDesc() + " - COST: " + str(self.useCost)
    

    def Use(self, target):
        stamina = gc.playerCharacter.stamina
        if (stamina < self.useCost):
            print("Not enough stamina to use item! Need " + str(self.useCost) + " stamina, has " + str(stamina) + " stamina.")
            return False
        
        gc.playerCharacter.stamina -= self.useCost
        print("Using " + self.name + " on " + target.name)
        pass


class Weapon(UseableItem):
    def __init__(self, name, rarity, useCost, damage):
        super().__init__(name, rarity, useCost)
        self.damage = damage


    def GetDesc(self):
        return super().GetDesc() + " - Damage: " + str(self.damage)
    

    def Use(self, target):
        if super().Use(target) == False:
            return False
        
        target.Damage(self.damage)


class HealthPotion(UseableItem):
    def __init__(self, name, rarity, useCost, healing):
        super().__init__(name, rarity, useCost)
        self.healing = healing


    def GetDesc(self):
        return super().GetDesc() + " - Healing: " + str(self.healing)


itemsList = [
    Weapon("Rusty Sword", 100, 2, 15),
    Weapon("Excalibur", 1, 2, 57),
    HealthPotion("Lesser Health Pot", 75, 1, 25),
    HealthPotion("Greater Health Pot", 30, 1, 50)
]