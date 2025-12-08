import RPG
import GameCore as gc
import inspect
import ItemSystem
import Items
import Entity
import Enemies
import CommandParam
from colorama import Fore, Back, Style
import Relics

# To-do: Create a more robust command paramter system, parameter type checking, hints
#        Dynamic command list depending on current environment

lastCommand = ""

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
    "inventory": Command("c_inventory", "Show and manage your inventory").SetParams(CommandParam.Parameter("action (drop, use)", CommandParam.StringArgument, True), CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True)),
    "quit": Command("c_quit", "Quits the game (for cowards)."),
    "use": Command("c_use", "Use item on entity").SetParams(CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True), CommandParam.Parameter("entityIndex", CommandParam.IntArgument, True)),
    "entities": Command("c_entities", "Show a list of all entities in scene"),
    "endturn": Command("c_endTurn", "Ends your turn!"),
    "status": Command("c_status", "Display status of player"),
    "showinfo": Command("c_showinfo", "Show info of player at all times"),
    "clear": Command("c_clear", "Clears the console"),

    # CHEAT COMMANDS
    "give-item": Command("c_spawnitem", "Spawns item", True).SetParams(CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True), CommandParam.Parameter("amount", CommandParam.IntArgument, True)),
    "item-list": Command("c_itemlist", "Shows all items in game by index", True),
    "enemy-list": Command("c_entitylist", "Shows all entities in game by index", True),
    "spawn-enemy": Command("c_spawnenemy", "Spawn an enemy into the scene", True).SetParams(CommandParam.Parameter("enemyIndex", CommandParam.IntArgument, True), CommandParam.Parameter("level", CommandParam.IntArgument, True), CommandParam.Parameter("amount", CommandParam.IntArgument, True)),
    "god-mode": Command("c_godmode", "Toggle godmode", True),
    "kill-enemy": Command("c_killenemy", "Kills enemy", True).SetParams(CommandParam.Parameter("enemyIndex [-a for all]", CommandParam.IntArgument, True)),
    "delete-enemy": Command("c_deleteenemy", "Deletes enemy without \"killing\" them", True).SetParams(CommandParam.Parameter("enemyIndex [-a for all]", CommandParam.IntArgument, True)),
    "trigger-event": Command("c_event", "Triggers an event", True),
    "give-gold": Command("c_givegold", "Give gold", True).SetParams(CommandParam.Parameter("amount", CommandParam.IntArgument, False)),
    "give-relic": Command("c_giverelic", "Give relic", True).SetParams(CommandParam.Parameter("relicIndex", CommandParam.IntArgument, True)),
    "relic-list": Command("c_reliclist", "Shows all relics in game by index", True),
}

def c_clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def c_giverelic(arguments: list):
    if len(arguments) <= 0:
        c_reliclist()
        selection = input("Choose relic to give: ")
        if (not selection.isnumeric() or selection == ''):
            print("Invalid selection.")
            return
        relicIndex = int(selection)
    else:
        relicIndex = arguments[0].Get()
    relic = Relics.GetRelicByIndex(relicIndex)
    if relic is None:
        print("Invalid relic index!")
        return
    gc.playerCharacter.GiveRelic(relic)

def c_reliclist():
    index = 0
    print("Relics List: ")
    for relic in Relics.relicsList:
        print(str(index) + ": " + relic.name + " - " + relic.description)
        index += 1

def c_givegold(arguments: list):
    if len(arguments) <= 0:
        return
    amount = arguments[0].Get()
    gc.playerCharacter.GiveGold(amount)

def c_killenemy(arguments: list):
    if len(arguments) > 0:
        if (arguments[0].GetRaw() == "-a"):
            for ent in reversed(gc.enemiesInScene):
                ent.Kill()
            return
        entity = gc.GetEntityByIndex(arguments[0].Get() - 1)
        if entity != None:
            entity.Kill()
        return
    
    PrintOutEntityList()
    selection = input("Choose entity to kill: ")
    if (not selection.isnumeric() or selection == ''):
        return
    
    entity = gc.GetEntityByIndex(int(selection) - 1)
    if entity != None:
            entity.Kill()

def c_deleteenemy(arguments: list):
    if len(arguments) > 0:
        if (arguments[0].GetRaw() == "-a"):
            for ent in reversed(gc.enemiesInScene):
                gc.RemoveEnemyFromScene(ent)
            return
        entity = gc.GetEntityByIndex(arguments[0].Get() - 1)
        if entity != None:
            gc.RemoveEnemyFromScene(entity) # type: ignore
        return
    
    PrintOutEntityList()
    selection = input("Choose entity to delete: ")
    if (not selection.isnumeric() or selection == ''):
        return
    
    entity = gc.GetEntityByIndex(int(selection) - 1)
    if entity != None:
            gc.RemoveEnemyFromScene(entity) # type: ignore

def c_godmode():
    gc.godmode = not gc.godmode
    print(f"Godmode set to: {gc.godmode}")

def c_entitylist():
    print("Entity List: ")
    index = 0
    import EnemyList as EList
    for entity in EList.__enemy_pool__:
        print(f"{index}: {entity.name}")
        index += 1
    pass

def c_spawnenemy(arguments: list):
    import EnemyList
    paramCount = len(arguments)
    if paramCount > 0:
        enemyIndex = arguments[0].Get()
        enemyLevel = arguments[1].Get() if paramCount >= 2 else 1
        amountToSpawn = arguments[2].Get() if paramCount >= 3 else 1
        for i in range(amountToSpawn):
            gc.SpawnEnemy(Enemies.CreateEnemyByIndex(enemyIndex, enemyLevel))
        return
    
    c_entitylist()
    selection = input("Choose entity to spawn: ")
    if (not selection.isnumeric() or selection == ''):
        print("Invalid selection.")
        return
    entityIndex = int(selection)
    if entityIndex < 0 or entityIndex >= len(EnemyList.__enemy_pool__):
        print("Invalid selection.")
        return
    
    level = input("Choose level (default 1): ")
    if ((not level.isnumeric()) or level == ''):
        print("Defaulting level to 1")
        level = "1"

    count = input(f"Choose count to spawn (default 1, max {gc.MAX_ENEMIES_IN_SCENE}): ")
    if ((not count.isnumeric()) or count == ''):
        print("Defaulting level to 1")
        count = "1"
    elif int(count) > gc.MAX_ENEMIES_IN_SCENE:
        print(f"{count} exceeds max of {gc.MAX_ENEMIES_IN_SCENE}; setting to {gc.MAX_ENEMIES_IN_SCENE}")
        count = gc.MAX_ENEMIES_IN_SCENE
    
    for i in range(int(count)):
        gc.SpawnEnemy(Enemies.CreateEnemyByIndex(entityIndex, int(level)))


def c_showinfo():
    gc.showPlayerInfo = not gc.showPlayerInfo
    print(("Showing " if gc.showPlayerInfo else "Hiding ") + "player info!")


def c_itemlist():
    index = 0
    print("Items List: ")
    for item in ItemSystem.itemsList:
        print(f"{index}: [{item.tag}] {item.name}")
        index += 1
    pass


def c_spawnitem(arguments: list):
    if (len(arguments) <= 0):
        c_itemlist()
        selection = input("Choose item to spawn: ")
        if (not selection.isnumeric() or selection == ''):
            print("Invalid selection.")
            return
        itemIndex = int(selection)
    else:
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
    print("Gold: " + str(gc.playerCharacter.GetGold()))
    print(f"Evasion: {gc.playerCharacter.GetEvasion() * 100}%")
    print(f"Critical Chance: {round(gc.playerCharacter.critialHitChance * 100, 2)}%")
    print(f"Damage Multiplier: {round(gc.playerCharacter.outgoingDamageMultiplier * 100, 2)}%")
    print(f"Gold Multiplier: {round(gc.goldMultiplier * 100, 2)}%")
    print(f"Experience Multiplier: {round(gc.experienceMultiplier * 100, 2)}%")
    print(f"Loot Multiplier: {round((gc.additionalLootChance + 1) * 100, 2)}%")
    print(f"Damage Resistance: {round(gc.playerCharacter.GetDamageResist() * 100, 2)}%")

    effectsText = gc.playerCharacter.GetEffectListText()
    if effectsText != None:
        print(f"Effects: {effectsText}")

def c_endTurn():
    if not PromptYesNoQuestion("Are you sure you want to end your turn?", False):
        return
    print("Ending turn!")
    gc.EndPlayerTurn()


def c_entities():
    PrintOutEntityList()

def PrintOutEntityList():
    from Entity import AEntity
    effectsText = gc.playerCharacter.GetEffectListText()
    print(f"\nEntities on the map: \n1: Player [HP: {gc.playerCharacter.health}{gc.playerCharacter.GetShieldText()}] [LVL: {gc.playerCharacter.level}] {(effectsText) if effectsText != None else ''}")
    index = 2
    print("-"*40)
    for enemy in gc.enemiesInScene:
        if enemy.actionSet is None:
            continue
        action = enemy.actionSet.GetNextAction()
        actionText = "[Just chillin']"
        if action is not None:
            actionText = f"!![{Style.BRIGHT}{Fore.RED}{action.GetShortDesc()}{Style.RESET_ALL}]!!"

        # Handle effects text
        effectsText = enemy.GetEffectListText()


        print(f"{index}: {enemy.name} [HP: {enemy.health}{enemy.GetShieldText()}] [LVL: {enemy.level}]{enemy.GetAdditionalDesc()} {actionText}{(' ' + effectsText) if effectsText != None else ''}")
        index += 1

def c_event():
    import GameEvent as ge

    # List out all events in the game
    for i, event in enumerate(ge.__event_list__, 1):
        print(f"{i}. {event.name}")

    while True:
        choice = input("Choose event to trigger: ")
        if (choice.isdigit()):
            digit = int(choice) - 1
            if digit < 0 or digit >= len(ge.__event_list__):
                print("Invalid input.")
                continue

            event = ge.GetGameEventByIndex(digit)
            if (event != None):
                event.TriggerEvent()
                return

        c_clear()
        print("Invalid input.")

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

    print(f"\nYou can type \"{RPG.REPEAT_COMMAND}\" to repeat last command.")
    print(f"You can type \"help (command)\" to find out more info on a command!")
    print("You can shorten commands just like in Packet Tracer! (Except parameter arguments because I'm lazy.)")
    print("Command List:\n")
    for command in command_map:
        hidden = command_map[command].hide
        if (showHidden == False and hidden == True):
            continue
        if (hidden == True):
            print(Back.YELLOW, end='')
        print(command + " - " + command_map[command].help_text + Style.RESET_ALL + (f"{Style.BRIGHT}{Fore.YELLOW} HIDDEN COMMAND{Style.RESET_ALL}" if hidden == True else ""))
        pass


def c_quit():
    if PromptYesNoQuestion("Are you sure?", False):
        gc.gameRunning = False
        print("Quitting game...")


def c_inventory(args: list):
    PrintOutInventory()

    if (args == None or len(args) <= 0):
        return
    action = args[0].Get().lower()
    
    # Helper function to get item index from user
    def GetItemIndexFromUser(question: str) -> int:
        selection = input(question)
        if (not selection.isnumeric() or selection == ''):
            return GetItemIndexFromUser(question)
        return int(selection) - 1
    
    # Get item index either from args or prompt user
    index = args[1].Get() - 1 if len(args) > 1 else GetItemIndexFromUser(f"Select item index to {action} (leave blank to cancel): ")
    
    if action == "drop":
        if (index < 0 or index >= len(gc.playerCharacter.items)):
            print("Invalid item index!")
            return
        item = gc.playerCharacter.items[index]
        if PromptYesNoQuestion(f"Are you sure you want to drop \"{item.name}\"?", False):
            gc.playerCharacter.items.remove(item)
            print(f"Dropped \"{item.name}\" from inventory.")
    elif action == "use":
        c_use_item_param_only(index + 1)
    else:
        print("Invalid action for inventory command!")
    

def PrintOutInventory():
    index = 1
    print("Inventory:\n")
    print(f"[{Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.GetGold()} Gold{Style.RESET_ALL}]")
    for item in gc.playerCharacter.items:
        useableFlag = issubclass(type(item), ItemSystem.TargetUseableItem)
        text = ""
        if useableFlag:
            text += Back.RED if gc.playerCharacter.stamina < item.useCost else ""
        text += str(index) + ": " + "[" + item.tag.upper() + "] " + item.GetDesc()
        if (useableFlag and item.useCount > 0):
            text += " [" + str(item.useCount) + " Uses]"
        text += Style.RESET_ALL
        print(text)
        index += 1

    # Print out relics
    if len(gc.playerCharacter.relics) > 0:
        print("\nRelics:")
        index = 1
        for relic in gc.playerCharacter.relics:
            extraText = ""
            if type(relic) is Relics.SoulvesselJar:
                extraText = f" [{Fore.MAGENTA}{Style.BRIGHT}{Relics.SoulvesselJar.killsToFill - Relics.soulvesselJarKillsNeeded}/{Relics.SoulvesselJar.killsToFill}{Style.RESET_ALL}]"
            print(f"{index}: {Fore.MAGENTA}{Style.BRIGHT}{relic.name}{Style.RESET_ALL} - {Fore.MAGENTA}{relic.description}{Style.RESET_ALL}{extraText}")
            index += 1

def c_use(parameters):
    if len(parameters) <= 0 or parameters == None:
        c_use_no_params()
        return

    itemIndex = parameters[0].Get() - 1
    # Assume the target is the player if we don't provide a target
    if len(parameters) > 1:
        targetIndex = parameters[1].Get() - 1
    else:
        c_use_item_param_only(itemIndex)
        return

    if itemIndex >= len(gc.playerCharacter.items):
        print("Invalid item")
        return

    UseItemOn(itemIndex, targetIndex)
    pass

def UseItemOn(itemIndex, targetIndex: int | None):
    if (itemIndex >= len(gc.playerCharacter.items) or (targetIndex is not None and (targetIndex < 0 or targetIndex > len(gc.enemiesInScene)))):
        return
    item = gc.playerCharacter.items[itemIndex]
    target: Entity.AEntity | None = gc.GetEntityByIndex(targetIndex) if targetIndex is not None else None

    # check if item is a weapon and if target is player ask to confirm
    if (issubclass(type(item), ItemSystem.Weapon) and target == gc.playerCharacter):
        if not PromptYesNoQuestion("Are you sure you want to use a weapon on yourself?", False):
            return

    if (issubclass(type(item), ItemSystem.UseableItem) is False):
        print("Nothing happened! \"" + item.name + "\" is not a useable item!")
        return

    if (item is None):
        return
    
    isTargetItem = issubclass(type(item), ItemSystem.TargetUseableItem)

    if (targetIndex is not None and isTargetItem):
        item.Use(target)
        return
    
    item.Use()

def c_use_no_params():
    PrintOutInventory()
    index = input("Select item to use (leave blank to cancel): ")

    if (not index.isnumeric() or index == ''):
        return

    c_use_item_param_only(int(index) - 1)

def c_use_item_param_only(itemIndex: int):
    if (itemIndex >= len(gc.playerCharacter.items)):
        return
    item: ItemSystem.TargetUseableItem = gc.playerCharacter.items[itemIndex]
    if (not issubclass(type(item), ItemSystem.TargetUseableItem)):
        UseItemOn(itemIndex, None)
        return
    PrintOutEntityList()
    target = input("Select target to use on (leave blank to default player): ")
    if target.strip() == '':
        target = "1"

    if (not target.isnumeric() or target == ''):
        return

    UseItemOn(itemIndex, int(target) - 1)

def PromptYesNoQuestion(promptText: str = "Are you sure?", defaultResponse: bool = False, requireImplicitResponse: bool = False) -> bool:
    response = defaultResponse
    optionText = 'y/n' if requireImplicitResponse else ('Y/n' if defaultResponse else 'y/N')
    command = input(f"{promptText} ({optionText}): ")
    commandLeftBlank = command.strip() == ""

    # If we input nothing and we don't require an implicit response then go default
    if not requireImplicitResponse and commandLeftBlank:
        return defaultResponse
    
    # We now require a response OR we inputted something
    if commandLeftBlank and requireImplicitResponse:
        print("Invalid input.")
        return PromptYesNoQuestion(promptText, defaultResponse, requireImplicitResponse)

    # A lil jank but if we need to have an implicit response then I suppose we should look 
    # at the ENTIRE input for what we need otherwise we just get the first char
    if not commandLeftBlank:
        command = command.lower()[0] if requireImplicitResponse else command
    else:
        command = "y" if defaultResponse else "n"

    if command == "y":
        response = True
    elif command == "n":
        response = False
    else:
        print("Invalid input.")
        return PromptYesNoQuestion(promptText, defaultResponse, requireImplicitResponse)
        
    return response

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

