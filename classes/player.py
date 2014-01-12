class Player:
    """ This is the main player class """

    def __init__(self, name, socket):
        self.name = name
        self.socket = socket
        self.wordList = []
        self.score = 0
        self.isGameOver = False

    def __str__(self):
        ret = "Player("
        ret += str(self.name) + ","
        ret += str(self.socket) + ","
        ret += str(self.score) + ","
        ret += str(self.wordList) + ")"
        return ret

    def toJSON(self):
        ret = {
            'name': self.name,
            'score': self.score,
            'wordList': self.wordList
        }
        return ret
