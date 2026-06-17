import GameCore as gc
import Commands
from colorama import Fore, Style

# region Info
## DEVELOPED AND DESIGNED BY MAGNUSON WHEN HE WAS BORED IN CLASS
#   TODO:
#   1. Add ability to increase stats when leveling up
#   2. Add Relics that give bonuses or effects
#   3. Add Equipable equipment
#   4. Add different "rooms" ex: Boss room, trap room, shop room, normal enemy room, "endless" horde room
#   5. More enemies
#   6. More items and item types
##
# endregion

REPEAT_COMMAND = '!'

def main():
    Commands.c_clear()
    setup()
    GameLoop()

def setup():
    print("Welcome traveller!")
    gc.Init()

def GameLoop():
    while gc.gameRunning == True:
        command = GetInput()
        if (command == REPEAT_COMMAND):
            command = Commands.lastCommand
        PushInput(command)
        gc.CheckEncounterStillHasEnemies()

    print("Game over!")
    print(f"[Kills: {gc.killCount}] [Level Reached: {gc.playerCharacter.level.level}] [Difficulty: {gc.setDifficulty.name.title()}]")
    input("Press enter to exit...")

def GetInput() -> str:
    import SkillSystem
    if (gc.showPlayerInfo):
        skillPointTxt = "" if SkillSystem.playerSkillPoints <= 0 else f" [{Fore.CYAN}{Style.BRIGHT}{SkillSystem.playerSkillPoints}{Style.RESET_ALL} Skill points available!]"
        print(f"\n[{Fore.GREEN}{Style.BRIGHT}{gc.playerCharacter.name}{Style.RESET_ALL}] [HP: {Fore.RED}{Style.BRIGHT}{gc.playerCharacter.health}/{gc.playerCharacter.maxHealth}{Style.RESET_ALL}{gc.playerCharacter.GetBonusHealthText()}] [STAMINA: {Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.stamina}/{gc.playerCharacter.maxStamina}{Style.RESET_ALL}] [LVL: {Fore.CYAN}{Style.BRIGHT}{gc.playerCharacter.level}{Style.RESET_ALL}] [EXP: {Fore.WHITE}{Style.BRIGHT}{gc.playerCharacter.level.heldExperience}/{gc.playerCharacter.level.neededExperience}{Style.RESET_ALL}]{skillPointTxt}")
    command = input(("\n" if not gc.showPlayerInfo else "") + "What do you do next? (Type \"help\" for help!): ").lower()
    command = command.strip()
    return command

def PushInput(rawCommand: str):
    if (rawCommand != REPEAT_COMMAND):
        Commands.lastCommand = rawCommand
    commandSplit = rawCommand.split()
    print()
    if (len(rawCommand) <= 0 or len(commandSplit) <= 0):
        return
    Commands.ParseAndRun(commandSplit.pop(0), commandSplit)


if (__name__ == "__main__"):
    main()