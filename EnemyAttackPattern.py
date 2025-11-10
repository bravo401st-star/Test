class ActionSet():
    def __init__(self, *actions):
        if len(actions) <= 0:
            print("[ERROR] INVALID ACTION SET")
            return
        self.actions = []
        self.actionIndex = 0
        for action in actions:
            self.actions.append(action)
        
    def PerfermNextAction(self):
        self.actionIndex += 1
        if (self.actionIndex >= len(self.actions)):
            self.actionIndex = 0
