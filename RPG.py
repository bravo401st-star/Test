import GameCore as gc
import Items
import ItemSystem
import Commands

def main():
    setup()
    GameLoop()


def setup():
    print("Welcome traveller!")
    gc.playerCharacter.name = input("Please state your name: ")
    if gc.playerCharacter.name.strip() == "":
        gc.playerCharacter.name = "Player"
    print("\nI see... your name is " + gc.playerCharacter.name + "!"
           + "\n\nPlease take these items and begin your quest!!")
    gc.playerCharacter.GiveItem(Items.GetRandomItem(weighted=True))
    gc.playerCharacter.GiveItem(Items.GetItemByName("Rusty Sword"))


def GameLoop():
    while gc.gameRunning == True:
        command = input("\nWhat do you do next? (Type \"help\" for help!): ").lower()
        command = command.strip()
        commandSplit = command.split()
        Commands.ParseAndRun(commandSplit.pop(0), commandSplit)


    print("Game over!")


if (__name__ == "__main__"):
    main()