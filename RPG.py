import GameCore as gc
import Items
import Entity
import Commands
from colorama import Fore, Back, Style

def main():
    setup()
    GameLoop()


def setup():
    print("Welcome traveller!")
    gc.Init()



def GameLoop():
    while gc.gameRunning == True:
        if (gc.showPlayerInfo):
            print(f"\n[{Fore.GREEN}{Style.BRIGHT}{gc.playerCharacter.name}{Style.RESET_ALL}] [HP: {Fore.RED}{Style.BRIGHT}{gc.playerCharacter.health}/{gc.playerCharacter.maxHealth}{Style.RESET_ALL}] [STAMINA: {Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.stamina}/{gc.playerCharacter.maxStamina}{Style.RESET_ALL}] [LVL: {Fore.CYAN}{Style.BRIGHT}{gc.playerCharacter.level}{Style.RESET_ALL}] [EXP: {Fore.WHITE}{Style.BRIGHT}{gc.playerCharacter.level.heldExperience}/{gc.playerCharacter.level.neededExperience}{Style.RESET_ALL}]")
        command = input(("\n" if not gc.showPlayerInfo else "") + "What do you do next? (Type \"help\" for help!): ").lower()
        command = command.strip()
        commandSplit = command.split()
        print()
        if (len(command) <= 0 or len(commandSplit) <= 0):
            continue
        Commands.ParseAndRun(commandSplit.pop(0), commandSplit)

    print("Game over!")


if (__name__ == "__main__"):
    main()