import GameCore as gc
import Items
import Entity
import Commands
from colorama import Fore, Back, Style

## DEVELOPED AND DESIGNED BY MAGNUSON WHEN HE WAS BORED IN CLASS
#   TODO:
#   1. Add ability to increase stats when leveling up
#   2. Add Relics that give bonuses or effects
#   3. Add Equipable equipment
#   4. Add different "rooms" ex: Boss room, trap room, shop room, normal enemy room, "endless" horde room
#   5. More enemies
#   6. More items and item types
##
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
        if (command == "!"):
            command = Commands.lastCommand
        else:
            Commands.lastCommand = command
        commandSplit = command.split()
        print()
        if (len(command) <= 0 or len(commandSplit) <= 0):
            continue
        Commands.ParseAndRun(commandSplit.pop(0), commandSplit)

    print("Game over!")


if (__name__ == "__main__"):
    main()