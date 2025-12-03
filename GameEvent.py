import random
from abc import ABC, abstractmethod
from colorama import Fore, Style

class AGameEvent(ABC):
    name = "Generic Event"
    chance = 100

    @abstractmethod
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

        print(f"{Fore.RED}You have triggered a hidden trap!{Style.RESET_ALL}")
        damage = random.randrange(5, 16)
        gc.playerCharacter.Damage(damage)
        print(f"You take {Style.BRIGHT}{Fore.RED}{damage}{Style.RESET_ALL} damage from the trap!")

class MineEvent(AGameEvent):
    name = "Mine Event"
    chance = 20

    def TriggerEvent(self):
        import GameCore as gc
        hasPickaxe = gc.playerCharacter.HasItem("Pickaxe")
        
        print(f"You run into a strange abandoned mine!\nWhat do you do?\n1. Leave\n2. Mine for resources! {f'[{Fore.RED}REQUIRES PICKAXE!{Style.RESET_ALL}]' if not hasPickaxe else ''}")
        while (True):
            choice = input("Choose your option: ")
            if (choice.isdigit()):
                choiceIndex = int(choice)

                if choiceIndex == 1:
                    return
                elif choiceIndex == 2 and hasPickaxe:
                    self.Mine()
                    return

            print("Invalid Option")

    def Mine(self):
        import Items
        import GameCore as gc
        items = []
        items.append(Items.GetItemByName("Silver Nugget"))
        items.append(Items.GetItemByName("Crystal Shard"))
        items.append(Items.GetItemByName("Gold Ore"))
        items.append(Items.GetItemByName("Mithril Fragment"))
        items.append(Items.GetItemByName("Moonstone"))
        items.append(Items.GetItemByName("Random Jewel"))
        items.append(Items.GetItemByName("Rare Gemstone"))
        items.append(Items.GetItemByName("Obsidian Shard"))
        items.append(Items.GetItemByName("Diamond"))
        items.append(Items.GetItemByName("Gravel Piece"))
        
        for i in range(random.randint(3, 7)):
            gc.playerCharacter.GiveItem(items[random.randint(0, len(items) - 1)])
        pass


class StrangeCathedral(AGameEvent):
    name = "Strange Cathedral"
    chance = 10

    def TriggerEvent(self):
        import Commands
        import GameCore as gc
        import time
        failed = False
        hasKey = gc.playerCharacter.HasItem('Rusted Cathedral Key')
        print(f"{Style.BRIGHT}{Fore.MAGENTA}The forest thins, and a massive cathedral emerges from the fog—its spires cracked, its doors half-sunken into the earth.\n A faint glow flickers behind the shattered stained glass, like something still lives within.{Style.RESET_ALL}")
        while (True):
            print(f"What do you do?\n1. Approach the cathedral door.\n2. Circle the outside a look for another entrance. ({f'{Fore.RED}10%{Style.RESET_ALL}' if not failed else f'{Fore.RED}0%{Style.RESET_ALL}' })\n3. Leave it alone and continue on...")
            choice = input("Choose your option: ")
            if choice.isdigit():
                choiceIndex = int(choice)
                if choiceIndex == 1:
                    Commands.c_clear()
                    print(f"You approach the rusted door, {f'{Fore.YELLOW}a similar rust to a key you obtained before.{Style.RESET_ALL}' if hasKey else 'you study the design.'}")
                    time.sleep(2)
                    while (True):
                        text2 = f"\n3. Unlock with {Fore.MAGENTA}\"Rusted Cathedral Key\"{Style.RESET_ALL}"
                        print(f"What do you do?\n1. Leave\n2. Attempt to pick lock with your picklock ({Fore.RED}50%{Style.RESET_ALL})(x{gc.playerCharacter.GetItemCount('Lockpick Set')}){text2 if hasKey else ''}")
                        choice = input("Choose your option: ")
                        if choice.isdigit():
                            choiceNum = int(choice)
                            if choiceNum == 1:
                                return
                            elif choiceNum == 2:
                                if not gc.playerCharacter.HasItem("Lockpick Set"):
                                    print("You do not have a lockpick...")
                                    continue
                                gc.playerCharacter.RemoveItem("Lockpick Set")
                                if random.random() <= 0.5:
                                    self.SuccessfullyEntered()
                                    return
                                print(f"{Fore.RED}Your lockpick breaks!{Style.RESET_ALL}")
                            elif choiceNum == 3 and hasKey:
                                gc.playerCharacter.RemoveItem("Rusted Cathedral Key")
                                self.SuccessfullyEntered()
                                return
                            pass
                        print("Invalid Input.")
                    pass
                if choiceIndex == 2 and not failed:
                    if (random.random() <= 0.1):
                        break
                    else:
                        failed = True
                        print(f"{Fore.RED}You failed to find anything else of interest.{Style.RESET_ALL}")
                        time.sleep(2)
                if choiceIndex == 3:
                    return

            Commands.c_clear()
            print("Invalid input.")
        self.SuccessfullyEntered()
       

    def SuccessfullyEntered(self):
        import Commands
        import GameCore as gc
        Commands.c_clear()

        # At this point the player either found a way around or unlocked the door
        print(f"You step into the cathedral’s hollow silence. Dust hangs like fog, and rows of cracked pews lean as if in prayer.\n {Fore.MAGENTA}At the far wall, a reliquary stands with a strange relic.{Style.RESET_ALL}")
        gc.GiveRelicReward(Commands)

        pass


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