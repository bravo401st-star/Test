import RPG
import GameCore as gc
import inspect
import ItemSystem
import Items
import Entity
import Enemies
import CommandParam
import Helper
from colorama import Fore, Back, Style
import Relics
import sys

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
    "inventory": Command("c_inventory", "Show and manage your inventory").SetParams(CommandParam.Parameter("action (drop, use, sort)", CommandParam.StringArgument, True), CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True)),
    "quit": Command("c_quit", "Quits the game (for cowards)."),
    "use": Command("c_use", "Use item on entity").SetParams(CommandParam.Parameter("itemIndex", CommandParam.IntArgument, True), CommandParam.Parameter("entityIndex", CommandParam.IntArgument, True)),
    "entities": Command("c_entities", "Show a list of all entities in scene"),
    "endturn": Command("c_endTurn", "Ends your turn!"),
    "status": Command("c_status", "Display status of player"),
    "showinfo": Command("c_showinfo", "Show info of player at all times"),
    "clear": Command("c_clear", "Clears the console"),
    "skills": Command("c_skills", "View and invest in skill trees"),
    "escape": Command("c_escape", "Attempt to escape from combat"),

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
    "give-skillpoint": Command("c_giveskillpoint", "Gives the player skill point(s)", True).SetParams(CommandParam.Parameter("amount", CommandParam.IntArgument, True)),
    "trigger-encounter": Command("c_triggerencounter", "Triggers an encounter", True)
}

def c_clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def _get_single_keypress(prompt: str = "") -> str:
    try:
        import msvcrt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        ch = msvcrt.getwch()
        # echo the key (and newline for Enter)
        if ch == '\r':
            sys.stdout.write('\n')
        else:
            sys.stdout.write(ch + '\n')
        sys.stdout.flush()
        return ch
    except Exception:
        return input(prompt)

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

def c_giveskillpoint(arguments: list):
    import SkillSystem

    amountToGive = 1
    if len(arguments) > 0:
        amountToGive = arguments[0].Get()

    SkillSystem.playerSkillPoints += amountToGive
    print(f"Giving {amountToGive} skill points to player!")
    pass

def _is_tree_in_progress(tree) -> bool:
    """Check if a tree has any unlocked nodes."""
    for node in tree.nodes:
        if node.IsUnlocked():
            return True
    return False

def _is_tree_complete(tree) -> bool:
    """Check if all nodes in a tree are fully maxed out."""
    for node in tree.nodes:
        if node.rank < node.maxRank:
            return False
    return True

def _get_tree_in_progress() -> int:
    """Find which tree is currently in progress. Returns -1 if none."""
    import SkillSystem
    for idx, tree in enumerate(SkillSystem.__skill_trees__):
        if _is_tree_in_progress(tree) and not _is_tree_complete(tree):
            return idx
    return -1

def _has_previous_node_maxed(tree, node_idx: int) -> bool:
    """Check if the previous node in the tree list is fully maxed. First node always returns True."""
    if node_idx == 0:
        return True
    prev_node = tree.nodes[node_idx - 1]
    return prev_node.rank == prev_node.maxRank

def _has_unmet_prerequisites(node) -> bool:
    """Check if a node's prerequisites are all met."""
    import SkillSystem
    if not hasattr(node, 'prerequisites') or not node.prerequisites:
        return False
    for prereq_id in node.prerequisites:
        prereq_node = SkillSystem.GetSkillNode(prereq_id)
        if prereq_node is None or not prereq_node.IsUnlocked():
            return True
    return False

def c_skills():
    import SkillSystem
    
    while True:
        c_clear()
        print(f"\n{Fore.CYAN}=== SKILL TREES ===")
        print(f"Available Points: {Fore.YELLOW}{SkillSystem.playerSkillPoints}{Style.RESET_ALL}\n")
        
        # Find which tree is in progress (if any)
        in_progress_idx = _get_tree_in_progress()
        
        # Display all trees with numeric indices and status
        for idx, tree in enumerate(SkillSystem.__skill_trees__):
            is_complete = _is_tree_complete(tree)
            in_progress = _is_tree_in_progress(tree)
            
            if is_complete:
                status = f"{Fore.GREEN}(Complete){Style.RESET_ALL}"
            elif in_progress:
                status = f"{Fore.YELLOW}(In Progress){Style.RESET_ALL}"
            else:
                status = ""
            
            print(f"{Fore.CYAN}[{idx + 1}] {Style.BRIGHT}{tree.name.upper()}{Style.NORMAL} - {tree.description}{' ' + status if status else ''}")
        print()
        
        # Select tree
        tree_choice = input(f"{Fore.GREEN}Select a tree (1-{len(SkillSystem.__skill_trees__)}) or press Enter to exit: {Style.RESET_ALL}")
        if not tree_choice or tree_choice.strip() == "":
            return
        
        if not tree_choice.isnumeric():
            print(f"{Fore.RED}Invalid selection!{Style.RESET_ALL}")
            continue
        
        tree_idx = int(tree_choice) - 1
        if tree_idx < 0 or tree_idx >= len(SkillSystem.__skill_trees__):
            print(f"{Fore.RED}Invalid tree index!{Style.RESET_ALL}")
            continue
        
        selected_tree = SkillSystem.__skill_trees__[tree_idx]
        
        # Inner loop for node selection in this tree
        while True:
            c_clear()
            # Display nodes in selected tree
            print(f"Available Points: {Fore.YELLOW}{SkillSystem.playerSkillPoints}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}[{selected_tree.name.upper()}]")
            for node_idx, node in enumerate(selected_tree.nodes):
                bullet = "●" if node.IsUnlocked() else "○"
                rank_display = f" ({Fore.CYAN}{node.rank}/{node.maxRank}{Fore.RESET})"
                # Check if this node is locked (previous node not fully maxed)
                is_locked = not _has_previous_node_maxed(selected_tree, node_idx)
                if is_locked:
                    print(f" {Back.RED}{Fore.CYAN}[{node_idx + 1}]{Style.RESET_ALL}{Back.RED} {bullet} {node.name}{rank_display} - {node.description}{Style.RESET_ALL}")
                else:
                    print(f" {Fore.CYAN}[{node_idx + 1}]{Style.RESET_ALL} {bullet} {node.name}{rank_display} - {node.description}")
            print()
            
            # Determine if we can invest in this tree
            can_invest = True
            if SkillSystem.playerSkillPoints <= 0:
                can_invest = False
            elif in_progress_idx != -1 and in_progress_idx != tree_idx:
                can_invest = False  # A different tree is in progress
            
            # Select node within tree - simplified: invest in the next available node only
            if not can_invest:
                # wait for any keypress and go back
                _get_single_keypress(f"{Fore.GREEN}Press any key to go back: {Style.RESET_ALL}")
                break
            else:
                key = _get_single_keypress(f"{Fore.GREEN}Press SPACE to invest in the next available node, or press Enter to go back: {Style.RESET_ALL}")

            # Handle Enter/back
            if key == '\r' or key == '\n' or key == '':
                break  # Go back to tree selection

            # Only accept 'I' or 'i' to invest
            if key.lower() != ' ':
                print(f"{Fore.RED}Invalid selection! Press SPACE to invest or Enter to go back.{Style.RESET_ALL}")
                input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                continue

            # Find the next investable node (first node that can rank up, whose previous is fully maxed, and whose prerequisites are met)
            next_idx = None
            next_node = None
            for idx2, candidate in enumerate(selected_tree.nodes):
                if not candidate.CanRankUp():
                    continue
                if not _has_previous_node_maxed(selected_tree, idx2):
                    continue
                if _has_unmet_prerequisites(candidate):
                    continue
                next_idx = idx2
                next_node = candidate
                break

            if next_node is None:
                print(f"{Fore.RED}No investable node available in this tree right now.{Style.RESET_ALL}")
                input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                continue

            # Invest a single rank into the next node
            next_node.OnRankUp()
            SkillSystem.playerSkillPoints -= 1
            print(f"{Fore.GREEN}✓ Invested in {next_node.name}! Rank now: {next_node.rank}/{next_node.maxRank}{Style.RESET_ALL}\n")

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
        print(f"{index}: {entity.name} [{Fore.RED}{Enemies.EvaluateEnemyDanger(entity)}{Fore.RESET}]")
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
    print(f"Evasion: {round(gc.playerCharacter.evasion * 100, 2)}%")
    print(f"Lifesteal: {round(gc.playerCharacter.lifesteal * 100, 2)}%")
    print(f"Critical Chance: {round(gc.playerCharacter.critialHitChance * 100, 2)}%")
    print(f"Critical Hit Damage Multiplier: {round(gc.playerCharacter.criticalHitMultiplier * 100, 2)}%")
    print(f"Additional Raw Damage: {gc.playerCharacter.additionalRawDamage}")
    print(f"Damage Multiplier: {round(gc.playerCharacter.outgoingDamageMultiplier * 100, 2)}%")
    print(f"Shield Multiplier: {round(gc.playerCharacter.shieldMultiplier * 100, 2)}%")
    print(f"Gold Multiplier: {round(gc.playerCharacter.goldMultiplier * 100, 2)}%")
    print(f"Experience Multiplier: {round(gc.playerCharacter.experienceMultiplier * 100, 2)}%")
    print(f"Loot Multiplier: {round((gc.playerCharacter.lootDropChance) * 100, 2)}%")
    print(f"Damage Resistance: {round(gc.playerCharacter.GetDamageResist() * 100, 2)}%")
    print(f"Healing: {round(gc.playerCharacter.healingMultiplier * 100, 2)}%")
    print(f"Damage Reflect: {round(gc.playerCharacter.damageReflect * 100, 2)}%")
    print(f"Thorns: {gc.playerCharacter.thorns}")

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
    from EnemyTags import EnemyTag
    effectsText = gc.playerCharacter.GetEffectListText()
    print(f"\nEntities on the map: \n1: Player {Helper.GenerateHealthbar(gc.playerCharacter)} [LVL: {gc.playerCharacter.level}] {(effectsText) if effectsText != None else ''}")
    index = 2
    print("─"*50)
    for enemy in gc.enemiesInScene:
        if enemy.actionSet is None:
            continue
        action = enemy.actionSet.GetAction()
        actionText = "[Just chillin']"
        if action is not None:
            actionText = f"!![{Style.BRIGHT}{action.actionColor}{action.GetShortDesc()}{Style.NORMAL}{Fore.RESET}]!!{Style.RESET_ALL}"

        # Handle effects text
        effectsText = enemy.GetEffectListText()
        if enemy.stunCount > 0:
            actionText = f" {Fore.MAGENTA}{Style.BRIGHT}[STUNNED]{Style.RESET_ALL}"

        bossHint = f"{Fore.RED}🕱 " if enemy.HasTag(EnemyTag.BOSS) else Fore.RESET
        immunityHintColor = Back.LIGHTBLACK_EX if enemy.HasTag(EnemyTag.IMMUNE_TO_DAMAGE) else Back.RESET

        print(f"{immunityHintColor}{index}: {bossHint}{enemy.name}{Fore.RESET} {Helper.GenerateHealthbar(enemy)} [LVL: {enemy.level}]{enemy.GetAdditionalDesc()} {actionText}{(' ' + effectsText) if effectsText != None else ''}")
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

def c_triggerencounter():
    import Encounters as enc
    
    allEncounters = enc.GetAllEncounters()
    
    while True:
        for i, encounter in enumerate(allEncounters, 1):
            print(f"{i}. {encounter.name}\n\t˪{encounter.description}\n")
        choice = input("Enter encounter number: ")
        if (choice.isdigit()):
            digit = int(choice) - 1
            if digit < 0 or digit >= len(allEncounters):
                print("Invalid input.")
                continue

            encounter = allEncounters[digit]
            gc.StartEncounter(encounter)
            return

        c_clear()
        print("Invalid input.")

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
    
    if action == "sort":
        weapons = [i for i in gc.playerCharacter.items if isinstance(i, ItemSystem.Weapon)]
        shielding = [i for i in gc.playerCharacter.items if isinstance(i, ItemSystem.ShieldItem)]
        potions = [i for i in gc.playerCharacter.items if isinstance(i, ItemSystem.Potion)]
        other = [i for i in gc.playerCharacter.items if i not in weapons and i not in potions and i not in shielding]
        gc.playerCharacter.items = weapons + shielding + potions + other
        print(f"Sorted inventory!")
        return
    
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

def ForceEscape():
    # clear enemies from scene
        for enemy in reversed(gc.enemiesInScene):
            gc.RemoveEnemyFromScene(enemy)
        gc.CheckHandleEncounterEnd(False)

def ValidateEscapability() -> bool:
    if gc.currentEncounterReference == None:
        print("You can only escape during an encounter!")
        return False
    
    if gc.currentEncounterReference.escapeAllowed == False:
        print(f"{Fore.RED}{Style.BRIGHT}Escape is not allowed in this encounter!{Style.RESET_ALL}")
        return False
    return True

def c_escape():
    import random
    if not ValidateEscapability():
        return

    escapeChance = 0.1
    escapeChance += gc.playerCharacter.evasion * 0.5 # Evasion should contribute to escape chance
    if PromptYesNoQuestion(f"Are you sure you want to attempt an escape? [{Fore.RED}{Style.BRIGHT}{escapeChance * 100:.0f}%{Style.RESET_ALL}] (Costs 1 stamina)", False):
        if gc.playerCharacter.stamina <= 0:
            print("Not enough stamina to escape!")
            return
        gc.playerCharacter.stamina -= 1
        if random.random() < escapeChance:
            ForceEscape()
        else:
            print("Escape failed!")
    

def PrintOutInventory():
    index = 1
    print("Inventory:\n")
    print(f"[{Fore.YELLOW}{Style.BRIGHT}{gc.playerCharacter.GetGold()} Gold{Style.RESET_ALL}]")
    for item in gc.playerCharacter.items:
        useableFlag = issubclass(type(item), ItemSystem.UseableItem)
        text = ""
        if useableFlag:
            backFill = Back.CYAN if (gc.playerCharacter.bonusAttacks > 0 and issubclass(type(item), ItemSystem.Weapon)) else Back.RED
            text += backFill if gc.playerCharacter.stamina < item.useCost else ""
        text += str(index) + ": " + "[" + item.tag.upper() + "] " + item.GetDesc()
        if (useableFlag and item.useCount > 0):
            text += f" [{Fore.YELLOW}" + str(item.useCount) + f" Use{'s' if item.useCount > 1 else ''}{Fore.RESET}" + "]"
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

            if type(relic) is Relics.SoulbinderCharm:
                extraText = f" [{Fore.MAGENTA}{Style.BRIGHT}{Relics.SoulbinderCharm.soulbinderCharmGuaranteedRelicDropCounter}/{Relics.SoulbinderCharm.GUARANTEED_RELIC_DROP_KILLS}{Style.RESET_ALL}]"
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
        import random, StatusEffect
        if gc.playerCharacter.HasEffect(StatusEffect.MadnessEffect) and random.random() < 0.5: # 50% chance to target random entity instead of chosen target
            target = gc.playerCharacter # target player instead
            print(f"{Fore.MAGENTA}{Style.BRIGHT}Madness causes you to lose control of the item and use it on {target.name}!{Style.RESET_ALL}")
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
    target = input(f"Select target to use {Fore.GREEN}{item.name}{Fore.RESET} on (leave blank to default player): ")
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
        if command_map[found[0]].hide == True:
            gc.usedCheats = True
    else:
        print("Invalid command!")

