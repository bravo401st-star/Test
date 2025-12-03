import random
import Items
import ItemSystem
import GameCore as gc
import Commands
from colorama import Fore, Style
import Relics

class Shop:
    def __init__(self, inventorySize: int = 5):
        self.inventory: list[ItemSystem.AItem] = []
        hasRelic = gc.playerCharacter.HasRelic(Relics.GildedCompass)
        inventorySize += 1 if hasRelic else 0
        self.GenerateInventory(inventorySize)
        self.discount = (1 - Relics.GildedCompass.SHOP_DISCOUNT) if hasRelic else 1.0
        pass

    def GenerateInventory(self, numItems: int):
        self.inventory.clear()
        for _ in range(numItems):
            item = Items.GetRandomItem(weighted=True, rolls=1, blackList=[ItemSystem.JunkItem])
            self.inventory.append(item)
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
            print("5. Exit Shop")
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
                if Commands.PromptYesNoQuestion("Are you sure you want to leave?", False):
                    print("Thank you for visiting my shop!")
                    return
            else:
                print("Invalid choice. Please try again.")

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
            if issubclass(type(item), ItemSystem.LevelableItem):
                levelableItems.append(item)

        # List out items in inventory
        for index, item in enumerate(levelableItems):
            cost = int(item.GetGoldCost() * self.discount) * item.itemLevel
            priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
            print(f"{index + 1}. {priceTag} {item.GetDesc()}")

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
                cost = int(itemToBuy.GetGoldCost() * self.discount) * itemToBuy.itemLevel
                if gc.playerCharacter.SpendGold(cost):
                    itemToBuy.Upgrade()
                    print(f"{itemToBuy.name} has been upgraded to level {itemToBuy.itemLevel}!")
            else:
                print("Invalid item selection.")
        
        self.OpenShop()

    def BuyItems(self):
        self.PrintMoney()
        print("Here are the items available for purchase:")
        
        # List out items in inventory
        for index, item in enumerate(self.inventory):
            cost = int(item.GetGoldCost() * self.discount)
            priceTag = f"[{Fore.GREEN if gc.playerCharacter.CanAfford(cost) else Fore.RED}{Style.BRIGHT}{cost} gold{Style.RESET_ALL}]"
            print(f"{index + 1}. {priceTag} {item.GetDesc()}")

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
                cost = int(itemToBuy.GetGoldCost() * self.discount)
                if gc.playerCharacter.SpendGold(cost):
                    gc.playerCharacter.GiveItem(itemToBuy)
                    self.inventory.pop(choiceIndex)
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
            sellPrice = item.GetGoldCost() // 2
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
            gc.playerCharacter.GiveGold(item.GetGoldCost() // 2)