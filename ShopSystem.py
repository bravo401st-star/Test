import random
import Items
import ItemSystem
import GameCore as gc
import Commands

class Shop:
    def __init__(self, inventorySize: int = 5):
        self.inventory: list[ItemSystem.Item] = []
        self.GenerateInventory(inventorySize)
        pass

    def GenerateInventory(self, numItems: int):
        self.inventory.clear()
        for _ in range(numItems):
            item = Items.GetRandomItem(weighted=True)
            self.inventory.append(item)
        pass

    def OpenShop(self):
        print("Welcome strange traveller! What would you like to do?")
        while True:
            print("1. Buy Items")
            print("2. Sell Items")
            print("3. Exit Shop")
            choice = input("Enter your choice: ")

            Commands.c_clear()
            if choice == "1":
                self.BuyItems()
                return
            elif choice == "2":
                self.SellItems()
                return
            elif choice == "3":
                print("Thank you for visiting my shop!")
                return
            else:
                print("Invalid choice. Please try again.")

    def BuyItems(self):
        print("Here are the items available for purchase:")
        
        # List out items in inventory
        for index, item in enumerate(self.inventory):
            cost = item.GetGoldCost()
            print(f"{index + 1}. {item.GetDesc()} - Price: {cost} gold")

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
                cost = itemToBuy.GetGoldCost()
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
        
        print("Here are your items available for sale:")
        for index, item in enumerate(gc.playerCharacter.items):
            sellPrice = item.GetGoldCost() // 2
            print(f"{index + 1}. {item.GetDesc()} - Sell Price: {sellPrice} gold")


        choice = input("\nEnter the item you wish to sell, or '0' to cancel: ")
        if choice.isdigit():
            choiceIndex = int(choice) - 1
            if choiceIndex == -1:
                print("Sale cancelled.")
                self.OpenShop()
                return
            if choiceIndex < len(gc.playerCharacter.items):
                itemToSell = gc.playerCharacter.items[choiceIndex]
                sellPrice = itemToSell.GetGoldCost() // 2
                gc.playerCharacter.GiveGold(sellPrice)
                gc.playerCharacter.items.pop(choiceIndex)
            else:
                print("Invalid item selection.")

        self.OpenShop()