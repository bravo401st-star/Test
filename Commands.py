import RPG
import GameCore as gc
import inspect
import ItemSystem
import Items
import Entity
import Enemies
import CommandParam
from colorama import Fore, Back, Style

# To-do: Create a more robust command paramter system, parameter type checking, hints
#        Dynamic command list depending on current environment

class Command():
    def __init__(self, commandFunc: str, help_text: str, hide: bool = False):
        self.commandFunc = commandFunc
        self.help_text = help_text
        self.hide = hide
        self.params = None

    def Execute(self, rawArgs: list) -> bool:
        if (self.commandFunc in globals()):
            func = globals()[self.commandFunc]

            # skip parsing parameters if we don't need them
            if len(inspect.signature(func).parameters) <= 0:
                func()
                return True

            # check arguments with parameters and build argument list
            arguments = []
            index = 0

            if self.params == None or len(self.params) <= 0:
                func(arguments)
                return True

            for param in self.params:
                arg = None
                if index < len(rawArgs):
                    arg = rawArgs[index] # get arg
                if param.optional == False and arg == None:
                    print("Missing required arguments!")
                    return False
                if (arg == None):
                    continue
                arguments.append(param.CreateArg(rawArgs[index]))
                index += 1

            func(arguments)
            return True
        else:
            print("Command not implemented! (Oops!)")

        return False
    
    def GetCommandSyntax(self) -> str:
        if self.params == None:
            return ""
        syntax = ""
        for param in self.params:
            syntax += f", {Fore.YELLOW if param.optional else Fore.WHITE}{param.name}{Style.RESET_ALL}"
        syntax = syntax[2:] # probably a better way but idc I'm cutting out the first comma and space here
        return f"({syntax})"

    def SetParams(self, *params):
        if len(params) <= 0:
            print("[ERROR] No params given for command")
            return
        
        # verify the order of params has non-optionals first BEFORE optionals
        foundOptionalFlag = False
        for param in params:
            if not issubclass(type(param), CommandParam.Parameter):
                raise TypeError(f"Command parameter must be of type {CommandParam.Parameter}")
            if (foundOptionalFlag == True and param.optional == False):
                raise SyntaxError("Invalid Parameters (Must place optional params last)")
            if param.optional == True:
                foundOptionalFlag = True
        
        self.params = params
        return self
    
command_map = {
    "help": Command("c_help", "Shows all avaliable commands").SetParams(CommandParam.Parameter("command", CommandParam.StringArgument, True)),
    "inventory": Command("c_inventory", "Shows your current inventory"),
    "quit": Command("c_quit", "Quits the game (for cowards)."),
    "use": Command("c_use", "Use item on entity").SetParams(CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True), CommandParam.Parameter("entityIndex", CommandParam.IntArgument, True)),
    "entities": Command("c_entities", "Show a list of all entities in scene"),
    "endturn": Command("c_endTurn", "Ends your turn!"),
    "status": Command("c_status", "Display status of player"),
    "showinfo": Command("c_showinfo", "Show info of player at all times"),

    # CHEAT COMMANDS
    "spawn-item": Command("c_spawnitem", "Spawns item", True).SetParams(CommandParam.Parameter("itemIndex", CommandParam.IntArgument, False), CommandParam.Parameter("amount", CommandParam.IntArgument, True)),
    "item-list": Command("c_itemlist", "Shows all items in game by index", True),
    "spawn-enemy": Command("c_spawnenemy", "Spawn an enemy into the scene", True).SetParams(CommandParam.Parameter("enemyIndex", CommandParam.IntArgument, False), CommandParam.Parameter("level", CommandParam.IntArgument, True)),
    "god-mode": Command("c_godmode", "Toggle godmode", True)
}

def c_godmode():
    gc.godmode = not gc.godmode
    print(f"Godmode set to: {gc.godmode}")

def c_spawnenemy(arguments: list):
    enemyIndex = arguments[0].Get()
    level = arguments[1].Get() if len(arguments > 1) else 1
    gc.SpawnEnemy(Enemies.CreateEnemyByIndex(enemyIndex, level))
    pass


def c_showinfo():
    gc.showPlayerInfo = not gc.showPlayerInfo
    print(("Showing " if gc.showPlayerInfo else "Hiding ") + "player info!")


def c_itemlist():
    index = 0
    print("Items List: ")
    for item in ItemSystem.itemsList:
        print(str(index) + ": " + item.name)
        index += 1
    pass


def c_spawnitem(arguments: list):
    if (len(arguments) <= 0):
        return
    itemIndex = arguments[0].Get()
    amount = arguments[1].Get() if len(arguments) > 1 else 1
    if (amount > 8):
        print("Limiting amount spawned to '8' to save sanity.")
        amount = 8

    for i in range(0, amount):
        gc.playerCharacter.GiveItem(Items.GetItemByIndex(itemIndex))

    pass


def c_status():
    print(gc.playerCharacter.name + " status:\n")
    print("Health: " + str(gc.playerCharacter.health))
    print("Stamina: (" + str(gc.playerCharacter.stamina) + "/" + str(gc.playerCharacter.maxStamina) + ")")
    print("Level: " + str(gc.playerCharacter.level))
    print(f"Experience: {gc.playerCharacter.level.heldExperience}/{gc.playerCharacter.level.neededExperience}")


def c_endTurn():
    print("Ending turn!")
    gc.EndPlayerTurn()


def c_entities():
    PrintOutEntityList()

def PrintOutEntityList():
    print("\nEntities on the map: \n1: Player" + " [HP: " + str(gc.playerCharacter.health) + "]" + " [LVL: " + str(gc.playerCharacter.level) + "]")
    index = 2
    print("-"*40)
    for enemy in gc.enemiesInScene:
        print(f"{index}: {enemy.name} [HP: {enemy.health}] [LVL: {enemy.level}] !![{Style.BRIGHT}{Fore.RED}{enemy.actionSet.GetNextAction().GetShortDesc()}{Style.RESET_ALL}]!!")
        index += 1


def c_help(args: list):
    global command_map
    showHidden = False

    if len(args) > 0 and args[0].Get() == "-hidden":
        showHidden = True

    if (showHidden == False and len(args) > 0):
        print("-" * 20)
        command = command_map.get(args[0].Get())
        if (command == None):
            print(f"Command \"{args[0].Get()}\" does not exist!")
            print("-" * 20)
            return
        print(f"[{Fore.YELLOW}{Style.BRIGHT}OPTIONAL {Fore.WHITE}{Style.NORMAL}| {Style.BRIGHT}REQUIRED{Style.RESET_ALL}]\n{args[0].Get()} {command.GetCommandSyntax()}\n{command.help_text}")
        print("-" * 20)
        return

    print("\nCommand List:\n")
    for command in command_map:
        hidden = command_map[command].hide
        if (showHidden == False and hidden == True):
            continue
        if (hidden == True):
            print(Back.YELLOW, end='')
        print(command + " - " + command_map[command].help_text + Style.RESET_ALL + (f"{Style.BRIGHT}{Fore.YELLOW} HIDDEN COMMAND{Style.RESET_ALL}" if hidden == True else ""))
        pass


def c_quit():
    command = input("Are you sure? (Y/N): ")
    if command.lower()[0] == "y":
        gc.gameRunning = False
        print("Quitting game...")


def c_inventory():
    PrintOutInventory()

def PrintOutInventory():
    index = 1
    print("\nInventory:\n")
    for item in gc.playerCharacter.items:
        useableFlag = issubclass(type(item), ItemSystem.UseableItem)
        text = ""
        if useableFlag:
            text += Back.RED if gc.playerCharacter.stamina < item.useCost else ""
        text += str(index) + ": " + "[" + item.tag.upper() + "] " + item.GetDesc()
        if (useableFlag and item.useCount > 0):
            text += " [" + str(item.useCount) + " Uses]"
        text += Style.RESET_ALL
        print(text)
        index += 1
    print("\n")


def c_use(parameters):
    if len(parameters) <= 0 or parameters == None:
        c_use_no_params()
        return

    itemIndex = parameters[0].Get() - 1
    # Assume the target is the player if we don't provide a target
    targetIndex = (parameters[1].Get() - 1) if len(parameters) > 1 else 0

    if itemIndex >= len(gc.playerCharacter.items):
        print("Invalid item")
        return

    UseItemOn(itemIndex, targetIndex)
    pass

def UseItemOn(itemIndex, targetIndex):
    if (itemIndex >= len(gc.playerCharacter.items)):
        return
    item: ItemSystem.UseableItem = gc.playerCharacter.items[itemIndex]
    target: Entity.Entity = gc.GetEntity(targetIndex)

    if (issubclass(type(item), ItemSystem.UseableItem) is False):
        print("Nothing happened! \"" + item.name + "\" is not a useable item!")
        return

    if (item == None or target == None):
        return
    
    item.Use(target)

def c_use_no_params():
    PrintOutInventory()
    index = input("Select item to use (leave blank to cancel): ")

    if (not index.isnumeric or index == ''):
        return

    PrintOutEntityList()
    target = input("Select target to use on (leave blank to default player): ")
    if target.strip() == '':
        target = "1"

    UseItemOn(int(index) - 1, int(target) - 1)

    pass

def GetCommand(inputString: str) -> list:
    found = []
    for comm in command_map:
        # If command is hidden look for exact match to prevent accidental triggering
        if command_map[comm].hide:
            if comm == inputString:
                found.append(comm)
            continue
        # Get all commands that are similar to the input
        if (comm[:len(inputString)] == inputString):
            found.append(comm)
            pass
        pass

    return found


def ParseAndRun(command: str, arguments: list):
    global command_map

    if len(command) <= 0:
        return
    
    found = GetCommand(command)

    if len(found) <= 0:
        print("Invalid Command!")
        return
    
    if len(found) > 1:
        print("Command ambiguous between: " + str(found))
        return
    
    if (found[0] in command_map):
        command_map[found[0]].Execute(arguments)
    else:
        print("Invalid command!")

