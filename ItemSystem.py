import GameCore as gc

class Item():
    tag = "ITEM"

    def __init__(self):
        self.name = "Unnamed Item"
        self.rarity = 100
        pass
    
    def GetDesc(self):
        return self.name
    
    def SetName(self, name: str):
        self.name = name
        return self

    def SetRarity(self, rarity: int):
        self.rarity = rarity
        return self


class UseableItem(Item):
    def __init__(self):
        super().__init__()
        self.useCost = 1
        self.useCount = -1

    def GetDesc(self):
        return super().GetDesc() + " - COST: " + str(self.useCost)

    def Use(self, target):
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        stamina = gc.playerCharacter.stamina
        if (stamina < self.useCost):
            print("Not enough stamina to use item! Need " + str(self.useCost) + " stamina, has " + str(stamina) + " stamina.")
            return False
        
        gc.playerCharacter.stamina -= self.useCost
        print("Using " + self.name + " on " + target.name)

        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()
        pass

    def RemoveSelfFromInventory(self):
        if (self in gc.playerCharacter.items):
            gc.playerCharacter.items.remove(self)

    def SetUses(self, uses: int):
        self.useCount = uses
        return self
    
    def SetUseCost(self, cost: int):
        self.useCost = cost
        return self


class Weapon(UseableItem):
    tag = "WEAPON"

    def __init__(self):
        super().__init__()
        self.damage = 1

    def GetDesc(self):
        return super().GetDesc() + " - Damage: " + str(self.damage)

    def Use(self, target):
        if super().Use(target) == False:
            return False
        
        target.Damage(self.damage)

    def SetDamage(self, damage: int):
        self.damage = damage
        return self


class HealthPotion(UseableItem):
    tag = "POTION"

    def __init__(self):
        super().__init__()
        self.healing = 0


    def GetDesc(self):
        return super().GetDesc() + " - Healing: " + str(self.healing)
    

    def Use(self, target):
        if (target.health >= target.maxHealth):
            return False
        if super().Use(target) == False:
            return False
        
        target.Heal(self.healing)

    def SetHealing(self, healing: int):
        self.healing = healing
        return self


itemsList = [
    # Weapons
    Weapon().SetName("Rusty Sword").SetRarity(100).SetUseCost(2).SetDamage(15),
    Weapon().SetName("Excalibur").SetRarity(1).SetUseCost(2).SetDamage(50),

    # Potions
    HealthPotion().SetName("Lesser Health Potion").SetRarity(75).SetUseCost(1).SetUses(3).SetHealing(20),
    HealthPotion().SetName("Greater Health Potion").SetRarity(30).SetUseCost(1).SetUses(1).SetHealing(50),

    # Basic Items
    Item().SetName("Cloth Fragment").SetRarity(90)
]