import Items
import Entity
import Enemies
import random
from colorama import Fore, Back, Style

MAX_ENEMIES_IN_SCENE = 16

def Init():
    playerCharacter.name = input("Please state your name: ")
    if playerCharacter.name.strip() == "":
        playerCharacter.name = "Player"
    print("\nI see... your name is " + playerCharacter.name + "!"
           + "\n\nPlease take these items and begin your quest!!")
    playerCharacter.GiveItem(Items.GetItemByName("Rusty Sword"))
    playerCharacter.GiveItem(Items.GetItemByName("Lesser Health Potion"))

    SpawnEnemy(Enemies.CreateEnemyByName("Goblin"))

def SpawnEnemy(enemy: Entity.BasicEnemy | None, force: bool = False):
    global enemiesInScene
    global MAX_ENEMIES_IN_SCENE
    if enemy == None or (len(enemiesInScene) >= MAX_ENEMIES_IN_SCENE and not force):
        return
    enemiesInScene.append(enemy)
    enemy.OnSpawn()
    print(f"A [LVL {enemy.level}]" + Fore.RED + Style.BRIGHT + enemy.name + Style.RESET_ALL + " has appeared!")
    pass

def GetIndexOfEnemy(enemy: Entity.BasicEnemy) -> int:
    global enemiesInScene
    index = 1

    for en in enemiesInScene:
        index += 1
        if en is enemy:
            break

    return index

def GetEntityByIndex(index: int):
    global enemiesInScene

    if (index < 0 or index > len(enemiesInScene)):
        return None

    if (index == 0):
        return playerCharacter
    else:
        return enemiesInScene[index - 1]
    
def GetRandomEnemyByType(searchType: type) -> Entity.BasicEnemy | None:
    global enemiesInScene
    listOfType = []
    for enemy in enemiesInScene:
        if issubclass(type(enemy), searchType):
            listOfType.append(enemy)

    if (len(listOfType) <= 0):
        return None
    return listOfType[random.randrange(0, len(listOfType))]

def GetRandomEnemyByTag(searchTag: str) -> Entity.BasicEnemy | None:
    global enemiesInScene
    listOfTag = []
    for enemy in enemiesInScene:
        if issubclass(type(enemy), Entity.BasicEnemy) and enemy.HasTag(searchTag):
            listOfTag.append(enemy)

    if (len(listOfTag) <= 0):
        return None
    return listOfTag[random.randrange(0, len(listOfTag))]
    
def OnEntityDie(entity: Entity.AEntity | None):
    global gameRunning
    global killCount
    if entity == None:
        return
    if type(entity) is Entity.Player:
        print("You died!")
        gameRunning = False
        return
    
    if issubclass(type(entity), Entity.BasicEnemy):
        print(entity.name + " has died!")
        RemoveEnemyFromScene(entity)
        killCount += 1
        return
    pass
Entity.e_EntityDeath.Subscribe(OnEntityDie)

def RemoveEnemyFromScene(enemy):
    global enemiesInScene
    if enemy in enemiesInScene:
            enemiesInScene.remove(enemy)
            CheckEncounterStatus()
            return True
    return False

def GetCountOfEntityType(entityType: type) -> int:
    global enemiesInScene
    count = 0
    if not issubclass(entityType, Entity.AEntity):
        return count
    
    for entity in enemiesInScene:
        if issubclass(type(entity), entityType):
            count += 1

    return count

def GetAllEnemiesOfType(entityType: type) -> list | None:
    global enemiesInScene
    enemiesOfType = []
    if not issubclass(entityType, Entity.AEntity):
        return None
    
    for entity in enemiesInScene:
        if type(entity) is entityType:
            enemiesOfType.append(entity)

    return enemiesOfType

def CheckEncounterStatus():
    import Commands
    global enemiesInScene
    global playerCharacter
    if (len(enemiesInScene) > 0):
        return True
    
    rewardItem = Items.GetRandomItem(weighted=True)
    if (Commands.PromptYesNoQuestion(f"You have defeated all enemies in the area! You find a {Style.BRIGHT}{Fore.MAGENTA}{rewardItem.name}{Style.RESET_ALL} as a reward. Do you want to keep it?", True, True)):
        playerCharacter.GiveItem(rewardItem)

    EndPlayerTurn()
    ChooseNextEvent()

def ChooseNextEvent():
    import Commands
    eventRoll = random.randrange(0, 100)
    if (eventRoll < 50):
        print(f"{Fore.GREEN}You find a peaceful clearing. You take a moment to rest.{Style.RESET_ALL}")
        playerCharacter.health += int(playerCharacter.maxHealth * 0.2)
        if (playerCharacter.health > playerCharacter.maxHealth):
            playerCharacter.health = playerCharacter.maxHealth
        print(f"You recover some health! Current health: {Style.BRIGHT}{Fore.RED}{playerCharacter.health}/{playerCharacter.maxHealth}{Style.RESET_ALL}")
    elif (eventRoll < 80):
        print("You stumble upon a wandering merchant!")
        Commands.c_shop()
    
    # Next encounter
    print("You venture deeper into the wilderness...")
    for i in range(0, random.randrange(1, 4 + playerCharacter.level.level // 2)):
        level = max(1, playerCharacter.level.level + random.randrange(-1, 2))
        enemy = Enemies.CreateRandomEnemy(1, level)
        if enemy is not None: 
            SpawnEnemy(enemy)


def EndPlayerTurn():
    global playerCharacter
    ProcessEnemyTurn()
    print("\n\nNew turn!")
    playerCharacter.stamina = playerCharacter.maxStamina
    playerCharacter.DoTurn()
    pass


def ProcessEnemyTurn():
    global enemiesInScene
    import copy, time, os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    tmpList = copy.copy(enemiesInScene)

    # Don't bother if there are no enemies
    if len(tmpList) <= 0:
        return
    
    print("Processing enemy turn!\n")
    for enemy in tmpList:
        enemy.DoTurn()
        time.sleep(0.2)


playerCharacter = Entity.Player().SetName("Player").SetMaxHealth(100).SetHealth(100)
enemiesInScene = []
gameRunning = True
showPlayerInfo = True
godmode = False
killCount = 0