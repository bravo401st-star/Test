import RPG
import GameCore as gc
import inspect
import ItemSystem
import Items
import Entity
import Enemies

# To-do: Create a more robust command paramter system, parameter type checking, hints
#        Dynamic command list depending on current environment

class Command():
    def __init__(self, commandFunc: str, help_text: str, hide: bool = False):
        self.commandFunc = commandFunc
        self.help_text = help_text
        self.hide = hide

    def Execute(self, arguments):
        if (self.commandFunc in globals()):
            func = globals()[self.commandFunc]
            if len(inspect.signature(func).parameters) > 0:
                if (len(arguments) <= 0):
                    print("No arguments provided!")
                    return
                func(arguments)
            else:
                func()
        else:
            print("Command not implemented! (Oops!)")

    
command_map = {
    "help": Command("c_help", "Shows all avaliable commands"),
    "inventory": Command("c_inventory", "Shows your current inventory"),
    "quit": Command("c_quit", "Quits the game (for cowards)."),
    "use": Command("c_use", "Use item on entity (itemIndex, target)"),
    "entities": Command("c_entities", "Show a list of all entities in scene"),
    "endTurn": Command("c_endTurn", "Ends your turn!"),
    "status": Command("c_status", "Display status of player"),
    "showInfo": Command("c_showinfo", "Show info of player at all times"),

    # CHEAT COMMANDS
    "spawn-item": Command("c_spawnitem", "Spawns item (Cheat)", True),
    "item-list": Command("c_itemlist", "Shows all items in game by index", True),
    "spawn-enemy": Command("c_spawnenemy", "Spawn an enemy into the scene (index, level)", True)
}


def c_spawnenemy(arguments: list):
    if (len(arguments) != 2):
        return
    gc.SpawnEnemy(Enemies.CreateEnemyByIndex(int(arguments[0]), int(arguments[1])))
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
    gc.playerCharacter.GiveItem(Items.GetItemByIndex(int(arguments[0])))
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
    print("\nEntities on the map: \n1: Player" + " [HP: " + str(gc.playerCharacter.health) + "]" + "[LVL: " + str(gc.playerCharacter.level) + "]")
    index = 2
    print("-"*40)
    for enemy in gc.enemiesInScene:
        print(str(index) + ": " + enemy.name + " [HP: " + str(enemy.health) + "]" + "[LVL: " + str(enemy.level) + "]")
        index += 1
    print("\n")


def c_help():
    global command_map
    print("\nCommand List:\n")
    for command in command_map:
        if (command_map[command].hide == True):
            continue
        print(command + " - " + command_map[command].help_text)
        pass
    print("\n")


def c_quit():
    command = input("Are you sure? (Y/N): ")
    if command.lower()[0] == "y":
        gc.gameRunning = False
        print("Quitting game...")


def c_inventory():
    index = 1
    print("\nInventory:\n")
    for item in gc.playerCharacter.items:
        text = str(index) + ": " + "[" + item.tag.upper() + "] " + item.GetDesc()
        if (issubclass(type(item), ItemSystem.UseableItem) and item.useCount > 0):
            text += " [" + str(item.useCount) + " Uses]"
        print(text)
        index += 1
    print("\n")


def c_use(parameters):
    if (len(parameters) < 2):
        return
    
    itemIndex = int(parameters[0]) - 1
    targetIndex = int(parameters[1]) - 1

    if itemIndex >= len(gc.playerCharacter.items):
        print("Invalid item")
        return

    item: ItemSystem.UseableItem = gc.playerCharacter.items[itemIndex]
    target: Entity.Entity = gc.GetEntity(targetIndex)

    if (issubclass(type(item), ItemSystem.UseableItem) is False):
        print("Nothing happened! \"" + item.name + "\" is not a useable item!")
        return


    if (item == None or target == None):
        return
    
    item.Use(target)
    pass

def ParseAndRun(command: str, arguments: str):
    global command_map

    if len(command) <= 0:
        return
    
    found = []
    for comm in command_map:
        # If command is hidden look for exact match to prevent accidental triggering
        if command_map[comm].hide:
            if comm == command:
                found.append(comm)
            continue
        # Get all commands that are similar to the input
        if (comm[:len(command)] == command):
            found.append(comm)
            pass
        pass

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

