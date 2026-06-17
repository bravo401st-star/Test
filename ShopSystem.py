import random
import Items
import ItemSystem
import GameCore as gc
import Commands
from colorama import Fore, Style
import Relics

class Shop:
    shopPrices = 1.0
    shopSellPrice = 1.0
    shopItemsCount = 5
    shopRelicCount = 0

    def __init__(self):
        self.inventory: list[ItemSystem.AItem] = []
        self.relicsForSale: list[Relics.ARelic] = []
        self.GenerateInventory(Shop.shopItemsCount)
        pass

    def GenerateInventory(self, numItems: int):
        self.inventory.clear()
        for _ in range(numItems):
            item = Items.GetRandomItem(weighted=True, rolls=1, filter=Items.Filter(ItemSystem.JunkItem))
            self.inventory.append(item)

        for _ in range(Shop.shopRelicCount):
            relic = Relics.GetRandomRelic()
            if relic is not None:
                self.relicsForSale.append(relic)
        pass

    def PrintMoney(self):
        print(f"You have {Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.GetGold()}{Style.RESET_ALL} gold.")

    def OpenShop(self):
        print("Welcome strange traveller! What would you like to do?")
        self.PrintMoney()
        while True:
            print("1. Buy Items")
            print("2. Sell Items")
            print("3. Upgrade Items")
            print("4. Quick Sell Junk")
            print("5. Services")
            print("6. Exit Shop")
            choice = input("Enter your choice: ")

            Commands.c_clear()
            if choice == "1":
                self.BuyItems()
                return
            elif choice == "2":
                self.SellItems()
                return
            elif choice == "3":
                self.UpgradeItems()
                return
            elif choice == "4":
                self.QuickSellJunk()
                return
            elif choice == "5":
                self.Services()
                return
            elif choice == "6":
                if Commands.PromptYesNoQuestion("Are you sure you want to leave?", False):
                    print("Thank you for visiting my shop!")
                    return
            else:
                print("Invalid choice. Please try again.")

    def Services(self):
        healCost = 15
        removeStatusCost = 50
        healAmount = 35
        print("Welcome to the services section! What would you like to do?")
        while True:
            healPriceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(healCost) else Fore.RED}{Style.BRIGHT}{healCost} gold{Style.RESET_ALL}]"
            removeStatusPriceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(removeStatusCost) else Fore.RED}{Style.BRIGHT}{removeStatusCost} gold{Style.RESET_ALL}]"

            print(f"1. {healPriceTag} Heal {Style.BRIGHT}{Fore.GREEN}{healAmount}{Style.RESET_ALL} health")
            print(f"2. {removeStatusPriceTag} Remove all negative status effects")
            print("3. Exit Services")
            choice = input("Enter your choice: ")

            Commands.c_clear()
            if choice == "1":
                if gc.playerCharacter.SpendGold(healCost):
                    gc.playerCharacter.Heal(healAmount)
                    print("You have been healed!")
                else:
                    print("You don't have enough gold!")
                continue
            elif choice == "2":
                if gc.playerCharacter.SpendGold(removeStatusCost):
                    gc.playerCharacter.ClearStatusEffects(True)
                    print("All negative status effects have been removed!")
                else:
                    print("You don't have enough gold!")
                continue
            elif choice == "3" or choice == "":
                break
            else:
                print("Invalid choice. Please try again.")

        self.OpenShop()

    def QuickSellJunk(self):
        junkItems: list[ItemSystem.JunkItem] = []
        for item in gc.playerCharacter.items:
            if type(item) is ItemSystem.JunkItem:
                junkItems.append(item)

        for junkItem in junkItems:
            self.SellItem(junkItem)

        self.OpenShop()
        
    def UpgradeItems(self):
        self.PrintMoney()
        print("Choose an item to upgrade!")

        # Get all items that are able to be leveled up
        levelableItems: list[ItemSystem.LevelableItem] = []

        for item in gc.playerCharacter.items:
            if issubclass(type(item), ItemSystem.LevelableItem) and item.itemLevel < item.maxLevel:
                levelableItems.append(item)

        # List out items in inventory
        for index, item in enumerate(levelableItems):
            cost = int(item.GetGoldCost() * Shop.shopPrices) * item.itemLevel # type: ignore
            priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
            print(f"{index + 1}. {priceTag} {item.GetDesc()}") # type: ignore

        if len(levelableItems) <= 0:
            print(f"No upgradable items!")

        # Select item to buy
        choice = input("\nEnter the item you wish to upgrade, or '0' to cancel: ")
        if choice.isdigit():
            choiceIndex = int(choice) - 1
            if choiceIndex == -1:
                print("Purchase cancelled.")
                self.OpenShop()
                return
            if choiceIndex < len(levelableItems):
                itemToBuy: ItemSystem.LevelableItem = levelableItems[choiceIndex]
                cost = int(itemToBuy.GetGoldCost() * Shop.shopPrices) * itemToBuy.itemLevel # type: ignore
                if gc.playerCharacter.SpendGold(cost):
                    itemToBuy.Upgrade()
                    print(f"{itemToBuy.name} has been upgraded to level {itemToBuy.itemLevel}!") # type: ignore
            else:
                print("Invalid item selection.")
        
        Commands.c_clear()
        self.OpenShop()

    def BuyItems(self):
        self.PrintMoney()
        print("Here are the items available for purchase:")
        
        # List out items in inventory
        for index, item in enumerate(self.inventory):
            cost = int(item.GetGoldCost() * Shop.shopPrices)
            priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
            print(f"{index + 1}. {priceTag} {item.GetDesc()}")

        for index, relic in enumerate(self.relicsForSale):
            cost = int(1000 * Shop.shopPrices)
            priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
            print(f"{len(self.inventory) + index + 1}. {priceTag} {relic.name} - {relic.description}")

        # Select item to buy
        choice = input("\nEnter the item you wish to buy, or '0' to cancel: ")
        if choice.isdigit():
            choiceIndex = int(choice) - 1
            if choiceIndex == -1:
                print("Purchase cancelled.")
                self.OpenShop()
                return
            if choiceIndex < len(self.inventory):
                itemToBuy = self.inventory[choiceIndex]
                cost = int(itemToBuy.GetGoldCost() * Shop.shopPrices)
                if gc.playerCharacter.SpendGold(cost):
                    gc.playerCharacter.GiveItem(itemToBuy)
                    self.inventory.pop(choiceIndex)
            elif choiceIndex >= len(self.inventory) and choiceIndex < len(self.inventory) + len(self.relicsForSale):
                relicToBuy = self.relicsForSale[choiceIndex - len(self.inventory)]
                cost = int(1000 * Shop.shopPrices)
                if gc.playerCharacter.SpendGold(cost):
                    gc.playerCharacter.GiveRelic(relicToBuy)
                    self.relicsForSale.pop(choiceIndex - len(self.inventory))
            else:
                print("Invalid item selection.")
        
        self.OpenShop()

    def SellItems(self):
        # List player's items
        if len(gc.playerCharacter.items) <= 0:
            print("You have no items to sell.")
            self.OpenShop()
            return
        
        self.PrintMoney()
        print("Here are your items available for sale:")
        for index, item in enumerate(gc.playerCharacter.items):
            sellPrice = round((item.GetGoldCost() // 4) * Shop.shopSellPrice)
            sellPriceTag = f"[{Fore.YELLOW}{Style.BRIGHT}+{sellPrice} gold{Style.RESET_ALL}]"
            print(f"{index + 1}. {sellPriceTag} {item.GetDesc()}")

        choices = input("\nEnter the item(s) you wish to sell, or '0' to cancel: ").strip().split()
        toSell: list[ItemSystem.AItem] = []
        toSellHumanReadable = []
        for choice in choices:
            if choice.isdigit():
                choiceIndex = int(choice) - 1
                if choiceIndex < len(gc.playerCharacter.items):
                    toSell.append(gc.playerCharacter.items[choiceIndex])
                    toSellHumanReadable.append(gc.playerCharacter.items[choiceIndex].name)

        if Commands.PromptYesNoQuestion(f"Are you sure you want to sell: {toSellHumanReadable}?", False):
            for item in toSell:
                self.SellItem(item)

        self.OpenShop()

    def SellItem(self, item):
        try:
            gc.playerCharacter.items.remove(item)
        except Exception as e:
            print(e)
        else:
            gc.playerCharacter.GiveGold(round((item.GetGoldCost() // 4) * Shop.shopSellPrice))