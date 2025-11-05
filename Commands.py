import RPG
import GameCore as gc
import inspect
import ItemSystem

class Command():
    def __init__(self, commandFunc: str, help_text: str):
        self.commandFunc = commandFunc
        self.help_text = help_text

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
    "status": Command("c_status", "Display status of player")
}


def c_status():
    print(gc.playerCharacter.name + " status:\n")
    print("Health: " + str(gc.playerCharacter.health))
    print("Stamina: (" + str(gc.playerCharacter.stamina) + "/" + str(gc.playerCharacter.maxStamina) + ")")


def c_endTurn():
    print("Ending turn!")


def c_entities():
    print("\nEntities on the map: \n1: Player")
    index = 2
    for enemy in gc.enemiesInScene:
        print(str(index) + ": " + enemy.name)
        index += 1
    print("\n")


def c_help():
    global command_map
    print("\nCommand List:\n")
    for command in command_map:
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
        print(str(index) + ": " + item.GetDesc())
        index += 1
    print("\n")


def c_use(parameters):
    itemIndex = int(parameters[0]) - 1
    targetIndex = int(parameters[1]) - 1

    if itemIndex >= len(gc.playerCharacter.items):
        print("Invalid item")
        return

    item: ItemSystem.UseableItem = gc.playerCharacter.items[itemIndex]
    target: gc.Entity = gc.GetEntity(targetIndex)

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

