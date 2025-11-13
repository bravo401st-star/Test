import Items
import Entity
import Enemies
import random
from colorama import Fore, Back, Style

def Init():
    playerCharacter.name = input("Please state your name: ")
    if playerCharacter.name.strip() == "":
        playerCharacter.name = "Player"
    print("\nI see... your name is " + playerCharacter.name + "!"
           + "\n\nPlease take these items and begin your quest!!")
    playerCharacter.GiveItem(Items.GetItemByName("Rusty Sword"))
    playerCharacter.GiveItem(Items.GetRandomItem(weighted=True))
    SpawnEnemy(Enemies.CreateEnemyByName("Goblin"))

def SpawnEnemy(enemy: Entity.BasicEnemy):
    global enemiesInScene
    enemiesInScene.append(enemy)
    print(f"A [LVL {enemy.level}]" + Fore.RED + Style.BRIGHT + enemy.name + Style.RESET_ALL + " has appeared!")
    pass


def GetEntity(index: int):
    global enemiesInScene

    if (index < 0 or index > len(enemiesInScene)):
        return None

    if (index == 0):
        return playerCharacter
    else:
        return enemiesInScene[index - 1]
    
def OnEntityDie(entity: Entity):
    global gameRunning
    if type(entity) is Entity.Player:
        print("You died!")
        gameRunning = False
        return
    
    if type(entity) is Entity.BasicEnemy:
        print(entity.name + " has died!")
        RemoveEnemyFromScene(entity)
        return
    pass
Entity.e_EntityDeath.Subscribe(OnEntityDie)


def RemoveEnemyFromScene(enemy: Entity.BasicEnemy):
    global enemiesInScene
    if enemy in enemiesInScene:
            enemiesInScene.remove(enemy)
            CheckEncounterStatus()
            return True
    return False


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

    for i in range(0, random.randrange(1, 4)):
        SpawnEnemy(Enemies.CreateRandomEnemy())


def EndPlayerTurn():
    global playerCharacter
    ProcessEnemyTurn()
    print("\n\nNew turn!")
    playerCharacter.stamina = playerCharacter.maxStamina
    pass


def ProcessEnemyTurn():
    global enemiesInScene
    for enemy in enemiesInScene:
        enemy.DoTurn()
        pass
    pass


playerCharacter = Entity.Player().SetName("Player").SetMaxHealth(100).SetHealth(100)
enemiesInScene = []
gameRunning = True
showPlayerInfo = False
godmode = False