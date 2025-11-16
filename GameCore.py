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
    playerCharacter.GiveItem(Items.GetRandomItem(weighted=True))
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
    
def OnEntityDie(entity: Entity.Entity | None):
    global gameRunning
    if entity == None:
        return
    if type(entity) is Entity.Player:
        print("You died!")
        gameRunning = False
        return
    
    if issubclass(type(entity), Entity.BasicEnemy):
        print(entity.name + " has died!")
        RemoveEnemyFromScene(entity)
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
    if not issubclass(entityType, Entity.Entity):
        return count
    
    for entity in enemiesInScene:
        if issubclass(type(entity), entityType):
            count += 1

    return count

def GetAllEnemiesOfType(entityType: type) -> list | None:
    global enemiesInScene
    enemiesOfType = []
    if not issubclass(entityType, Entity.Entity):
        return None
    
    for entity in enemiesInScene:
        if type(entity) is entityType:
            enemiesOfType.append(entity)

    return enemiesOfType

def CheckEncounterStatus():
    global enemiesInScene
    global playerCharacter
    if (len(enemiesInScene) > 0):
        return True
    
    rewardItem = Items.GetRandomItem(weighted=True)
    while True:
        command = input("You found " + rewardItem.name + " in the loot! (Keep? Y/N): ")
        if len(command) <= 0:
            print("You must make a choice!")
            continue

        if command.lower()[0] == "y":
            playerCharacter.GiveItem(rewardItem)
            break
        else:
            if command.lower()[0] == "n":
                break

        print("You must make a choice!")
    

    EndPlayerTurn()

    for i in range(0, random.randrange(1, 6)):
        SpawnEnemy(Enemies.CreateRandomEnemy())


def EndPlayerTurn():
    global playerCharacter
    ProcessEnemyTurn()
    print("\n\nNew turn!")
    playerCharacter.stamina = playerCharacter.maxStamina
    pass


def ProcessEnemyTurn():
    global enemiesInScene
    import copy, time, os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    tmpList = copy.copy(enemiesInScene)
    print("Processing enemy turn!\n")
    time.sleep(1)
    for enemy in tmpList:
        enemy.DoTurn()
        time.sleep(0.2)


playerCharacter = Entity.Player().SetName("Player").SetMaxHealth(100).SetHealth(100)
enemiesInScene = []
gameRunning = True
showPlayerInfo = False
godmode = False