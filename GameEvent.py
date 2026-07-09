from math import floor
import random
from abc import ABC, abstractmethod
from colorama import Fore, Style

import Items
import ItemSystem
import Relics

class AGameEvent(ABC):
    name = "Generic Event"
    chance = 100

    @abstractmethod
    def TriggerEvent(self):
        print(f"Event Triggered: {self.name}")

class ShopEvent(AGameEvent):
    name = "Shop Encounter"
    chance = 50

    def TriggerEvent(self):
        import ShopSystem
        print("You stumble upon a wandering merchant!")
        shop = ShopSystem.Shop()
        shop.OpenShop()

class TreasureEvent(AGameEvent):
    name = "Treasure Encounter"
    chance = 30

    def TriggerEvent(self):
        import GameCore as gc
        import Commands
        Commands.c_clear()
        print(f"{Fore.YELLOW}You find a gilded treasure chest!{Style.RESET_ALL}")
        if Commands.PromptYesNoQuestion("Do you want to open it?", True, True):
            if (random.random() <= 0.5):
                # trigger a mimic encounter
                import Encounters as enc
                gc.StartEncounter(enc.MimicEncounter())
                return
            TreasureEvent.GetReward()
            return
        print("You leave the treasure behind and continue on your journey.")

    @classmethod
    def GetReward(cls):
        import GameCore as gc
        import Commands
        rewardItem = Items.GetRandomItem(True, 1, rarityRange=range(1, 35))
        if (Commands.PromptYesNoQuestion(f"You open the chest and find a {Style.BRIGHT}{Fore.MAGENTA}{rewardItem.name}{Style.RESET_ALL}. Do you want to keep it?", True)):
            gc.playerCharacter.GiveItem(rewardItem)
            print(f"You take the {rewardItem.name} and continue on your journey.")
            return

class RestEvent(AGameEvent):
    name = "Rest"
    chance = 50
    potionChance = 0.5

    def TriggerEvent(self):
        import GameCore as gc
        import Commands
        Commands.c_clear()
        print(f"{Fore.GREEN}You find a peaceful clearing. You take a moment to collect yourself.{Style.RESET_ALL}")
        print(f"1. Rest and recover 20% of your max health, currently {Fore.GREEN}{gc.playerCharacter.health}/{gc.playerCharacter.maxHealth}{Fore.RESET} HP")
        print(f"2. Forage for potion makings ({Fore.RED}{int(self.potionChance * 100)}%{Fore.RESET} chance to find a potion)")

        while True:
            choice = input("Choose your option: ")
            if choice.isdigit():
                index = int(choice)
                if index == 1:
                    healthRecovered = int(gc.playerCharacter.maxHealth * 0.2)
                    gc.playerCharacter.health += healthRecovered
                    if gc.playerCharacter.health > gc.playerCharacter.maxHealth:
                        gc.playerCharacter.health = gc.playerCharacter.maxHealth
                    print(f"You recover {Style.BRIGHT}{Fore.RED}{healthRecovered}{Style.RESET_ALL} HP!")
                    return
                elif index == 2:
                    if random.random() <= self.potionChance:
                        potion = Items.GetRandomItem(True, 1, Items.Filter(ItemSystem.Potion, isBlackList=False))
                        if potion is not None:
                            gc.playerCharacter.GiveItem(potion)
                            print(f"You forage through the herbs and find stuff for a {Style.BRIGHT}{Fore.MAGENTA}{potion.name}{Style.RESET_ALL}.")
                        else:
                            print("You find some herbs, but nothing you can bottle into a potion.")
                    else:
                        print("You search for ingredients but come up empty-handed.")
                    return
            print("Invalid input.")

class TrapEvent(AGameEvent):
    name = "Trap Encounter"
    chance = 15

    def TriggerEvent(self):
        from AttackInfo import AttInfo
        import GameCore as gc

        print(f"{Fore.RED}You have triggered a hidden trap!{Style.RESET_ALL}")
        damage = random.randrange(5, 16)
        if random.random() < gc.playerCharacter.evasion:
            print(f"{Fore.YELLOW}Lucky! You manage to avoid the trap and take no damage!{Style.RESET_ALL}")
            return
        gc.playerCharacter.Damage(AttInfo(damage))
        print(f"You take {Style.BRIGHT}{Fore.RED}{damage}{Style.RESET_ALL} damage from the trap!")

class GraveyardEvent(AGameEvent):
    name = "Graveyard Encounter"
    chance = 20

    def TriggerEvent(self):
        import GameCore as gc
        import Commands
        import Encounters as enc
        Commands.c_clear()
        chanceToFindLoot = 0.5

        print(f"You come across a small graveyard. The air is thick with sorrow and the scent of decay.\n"
                f"1. Pay respects at the graves\n"
                f"2. Search the graves for loot ({Fore.RED}{chanceToFindLoot * 100:.0f}%{Fore.RESET})\n"
                f"3. Leave")

        while True:
            choice = input("Choose your option: ")
            if choice.isdigit():
                index = int(choice)
                if index == 1:
                    print("You take a moment to pay your respects. You feel a sense of calm wash over you.")
                    gc.playerCharacter.ClearStatusEffects(True)
                    return
                elif index == 2:
                    if random.random() > chanceToFindLoot:
                        gc.StartEncounter(enc.HauntedGraveyard())
                        return
                    print("You search the graves and find some loot!")
                    itemsToGive = floor(gc.playerCharacter.lootDropChance)
                    percentLeft = gc.playerCharacter.lootDropChance - itemsToGive

                    if random.random() < percentLeft:
                        itemsToGive += 1
                    rolls = 2 if gc.playerCharacter.HasRelic(Relics.FortunesEmblem) else 1
                    for _ in range(0, itemsToGive):
                        rewardItem = Items.GetRandomItem(True, rolls)
                    if (Commands.PromptYesNoQuestion(f"You have defeated all enemies in the area! You find a {Style.BRIGHT}{Fore.MAGENTA}{rewardItem.name}{Style.RESET_ALL} as a reward. Do you want to keep it?", True)):
                        gc.playerCharacter.GiveItem(rewardItem)
                    return
                elif index == 3:
                    Commands.c_clear()
                    return
            
            print("Invalid input.")

class MysteriousBlacksmithEvent(AGameEvent):
    name = "Mysterious Blacksmith Encounter"
    chance = 15
    upgradeCost = 100
    upgradeTimes = 3

    def TriggerEvent(self):
        import GameCore as gc
        import ItemSystem, Items
        import Commands
        Commands.c_clear()

        print(f"You run into a strange man covered in grime. He offers you a deal.\n"
                f"1. Upgrade one random weapon {MysteriousBlacksmithEvent.upgradeTimes}x ({Fore.YELLOW if gc.playerCharacter.CanAfford(MysteriousBlacksmithEvent.upgradeCost) else Fore.RED}{MysteriousBlacksmithEvent.upgradeCost} gold{Fore.RESET})\n"
                "2. Trade one random weapon for a higher rarity weapon\n"
                "3. Tell him to f**k off")

        while True:
            choice = input("Choose your option: ")
            if choice.isdigit():
                index = int(choice)
                if index == 1:
                    # check the affordability
                    if not gc.playerCharacter.CanAfford(MysteriousBlacksmithEvent.upgradeCost):
                        print("You can not afford that.")
                        continue

                    # get a list of all weapons that CAN upgrade
                    upgradeableWeaponList = gc.playerCharacter.GetAllItemsOfType(ItemSystem.Weapon)
                    for item in upgradeableWeaponList:
                        if not item.CanUpgrade():
                            upgradeableWeaponList.remove(item)

                    if len(upgradeableWeaponList) <= 0:
                        print("You have no weapons to upgrade!")
                        continue
                    gc.playerCharacter.SpendGold(MysteriousBlacksmithEvent.upgradeCost)
                    weapon = random.choice(upgradeableWeaponList)
                    
                    weapon.Upgrade(MysteriousBlacksmithEvent.upgradeTimes)
                    Commands.c_clear()
                    print(f"Your {weapon.name} was upgraded {MysteriousBlacksmithEvent.upgradeTimes} times!")
                    return
                elif index == 2:
                    weapon = gc.playerCharacter.GetRandomItemOfType(ItemSystem.Weapon)
                    if weapon == None:
                        print("You have no weapons to trade.")
                        continue

                    rarity = weapon.rarity
                    betterItem = Items.GetRandomItem(True, 1, Items.Filter(ItemSystem.Weapon, False), max(rarity - 1, 1), [Items.GetItemByName(weapon.name)])
                    if betterItem == None:
                        print("Your weapon is already the greatest it can be.")
                        continue

                    gc.playerCharacter.items.remove(weapon)
                    gc.playerCharacter.GiveItem(betterItem)
                    print(f"Your {weapon.name} was traded for {betterItem.name}")
                    return
                elif index == 3:
                    Commands.c_clear()
                    return
            
            print("Invalid input.")
    pass

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

class HerbalistEvent(AGameEvent):
    name = "Herbalist Encounter"
    chance = 20

    def TriggerEvent(self):
        import Commands
        import GameCore as gc

        Commands.c_clear()
        shopCount = random.randint(2, 3)
        potionPool = [item for item in ItemSystem.itemsList if issubclass(type(item), ItemSystem.Potion)]
        if len(potionPool) <= 0:
            print("The herbalist has no potions to sell today.")
            return

        healthPotions = [item for item in potionPool if issubclass(type(item), ItemSystem.HealthPotion)]
        guaranteedHealth = None
        if len(healthPotions) > 0:
            guaranteedHealth = random.choice(healthPotions)

        remainingPool = [item for item in potionPool if item is not guaranteedHealth]
        remainingCount = shopCount - (1 if guaranteedHealth is not None else 0)
        shopPotions = []
        if guaranteedHealth is not None:
            shopPotions.append(guaranteedHealth)

        if remainingCount > 0 and len(remainingPool) > 0:
            shopPotions.extend(random.sample(remainingPool, min(remainingCount, len(remainingPool))))

        while True:
            Commands.c_clear()
            print(f"{Fore.GREEN}You meet a traveling herbalist sitting beside a bubbling cauldron.{Style.RESET_ALL}")
            print("The herbalist offers the following potions:")
            self.PrintMoney()
            for index, potion in enumerate(shopPotions):
                cost = int(potion.GetGoldCost())
                priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
                print(f"{index + 1}. {priceTag} {potion.GetDesc()}")

            print("0. Leave")
            choice = input("Choose a potion to buy: ")
            if choice.strip() == "":
                if Commands.PromptYesNoQuestion("Do you want to leave the herbalist?", False):
                    print("You decide to leave the herbalist.")
                    return
                continue
            if choice.isdigit():
                choiceIndex = int(choice) - 1
                if choiceIndex == -1:
                    if Commands.PromptYesNoQuestion("Do you want to leave the herbalist?", False):
                        print("You decide to leave the herbalist.")
                        return
                    continue
                if 0 <= choiceIndex < len(shopPotions):
                    potion = shopPotions[choiceIndex]
                    cost = int(potion.GetGoldCost())
                    if Commands.PromptYesNoQuestion(f"Buy {potion.name} for {cost} gold?", False):
                        if gc.playerCharacter.SpendGold(cost):
                            gc.playerCharacter.GiveItem(potion)
                            shopPotions.pop(choiceIndex)
                            print(f"You buy the {potion.name}.")
                            if len(shopPotions) == 0:
                                print("The herbalist has no more potions to sell.")
                                return
                            continue
                        else:
                            print("You can't afford that potion.")
                            continue
                    else:
                        print("Purchase cancelled.")
                        continue
            print("Invalid choice.")

    def PrintMoney(self):
        import GameCore as gc
        print(f"You have {Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.GetGold()}{Style.RESET_ALL} gold.")

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
        gc.GiveRelicReward()

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