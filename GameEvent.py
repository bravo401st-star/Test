import random
from abc import ABC, abstractmethod

class AGameEvent(ABC):
    name = "Generic Event"
    chance = 100

    def TriggerEvent(self):
        print(f"Event Triggered: {self.name}")

class ShopEvent(AGameEvent):
    name = "Shop Encounter"
    chance = 35

    def TriggerEvent(self):
        import ShopSystem
        print("You stumble upon a wandering merchant!")
        shop = ShopSystem.Shop()
        shop.OpenShop()

class RestEvent(AGameEvent):
    name = "Rest"
    chance = 50

    def TriggerEvent(self):
        import GameCore as gc
        from colorama import Fore, Style

        print(f"{Fore.GREEN}You find a peaceful clearing. You take a moment to rest.{Style.RESET_ALL}")
        healthRecovered = int(gc.playerCharacter.maxHealth * 0.2)
        gc.playerCharacter.health += healthRecovered
        if (gc.playerCharacter.health > gc.playerCharacter.maxHealth):
            gc.playerCharacter.health = gc.playerCharacter.maxHealth
        print(f"You recover {Style.BRIGHT}{Fore.RED}{healthRecovered}{Style.RESET_ALL} HP!")

class TrapEvent(AGameEvent):
    name = "Trap Encounter"
    chance = 15

    def TriggerEvent(self):
        import GameCore as gc
        from colorama import Fore, Style

        print(f"{Fore.RED}You have triggered a hidden trap!{Style.RESET_ALL}")
        damage = random.randrange(5, 16)
        gc.playerCharacter.Damage(damage)
        print(f"You take {Style.BRIGHT}{Fore.RED}{damage}{Style.RESET_ALL} damage from the trap!")


def GetGameEventByName(name: str) -> AGameEvent | None:
    for event in __event_list__:
        if event.name == name:
            return event()
    print("Unknown event: \"" + name + "\"")
    return None

def GetGameEventByIndex(index: int) -> AGameEvent | None:
    if (index >= len(__event_list__) or index < 0):
        return None
    return __event_list__[index]()

def GetRandomEvent(weighted: bool = True) -> AGameEvent | None:
    totalChance = 0
    for event in __event_list__:
        totalChance += event.chance if weighted else 1

    roll = random.randrange(0, totalChance)
    currentChance = 0
    for event in __event_list__:
        currentChance += event.chance if weighted else 1
        if (roll < currentChance):
            return event()
    return None

__event_list__ = AGameEvent.__subclasses__()