import constants


class Game:
    """ This is the main game class """

    def __init__(self, player1, player2, index):
        self.player1 = player1
        self.player2 = player2
        self.gameState = {}
        self.gameIndex = index

        # Create a new game
        self.create_new_game()

    def create_new_game(self):
        """ Initialize the game state and create a
            random game """

        gameLetterGrid = []
        gameLetterUsage = {}
        gameLetterStrength = {}

        for row in constants.ROW_TILES:

            row_list = []

            for col in constants.COLUMN_TILES:

                random_letter = random.choice(constants.LETTERS)
                gameLetterUsage[randomLetter] = 0
                gameLetterStrength[randomLetter] = constants.STRENGTH_0

                row_list.append(randomLetter)

            gameLetterGrid.append(row_list)

        gameState['grid'] = gameLetterGrid
        gameState['usage'] = gameLetterUsage
        gameState['strength'] = gameLetterStrength

    def __str__(self):
        """ Return a string version of the Game class """

        ret = "Game("
        ret += str(self.player1) + ","
        ret += str(self.player2) + ","
        ret += str(self.gameState) + ","
        ret += str(self.gameIndex)
        ret += ")"
        return ret

    def start_game(self):

        """ Send message to the players to start game """

        self.player1.socket.write_message(json.dumps({
            'command': 'start',
            'player1': self.player1.toJSON(),
            'player2': self.player2.toJSON(),
            'gameState': self.gameState
        }))

        self.player2.socket.write_message(json.dumps({
            'command': 'start',
            'player1': self.player1.toJSON(),
            'player2': self.player2.toJSON(),
            'gameState': self.gameState
        }))

    def submit(self, word, dictionary, socket):

        """ This function makes a change to the game state
            when the player makes a move """
        currentPlayer, otherPlayer = self.whichPlayer(socket)

        # Validate Move in game
        validation_result = constants.VALIDATION_OUTCOME_RIGHT

        if word in currentPlayer.wordList or word in otherPlayer.wordList:
            # Check if word already exists in list of words made
            validation_result = constants.VALIDATION_OUTCOME_EXISTING
        elif word not in dictionary:
            # Check if the word is a valid dictionary word
            validation_result = constants.VALIDATION_OUTCOME_WRONG

        # Send validation result
        validation_msg = {
            'command': constants.VALIDATED_COMMAND,
            'result': validation_result
        }

        currentPlayer.socket.write_message(validation_msg)

        if validation_result == constants.VALIDATION_OUTCOME_RIGHT:
            # Update Game State
            self.update_game_state()

            # Update Players with new Game State
            currentPlayer.socket.write_message(
                {
                    'command': constants.UPDATE_COMMAND,
                    'gameState': self.gameState,
                    'myState': currentPlayer.toJSON(),
                    'opponentState': otherPlayer.toJSON()
                }
            )

            otherPlayer.socket.write_message(
                {
                    'command': constants.UPDATE_COMMAND,
                    'gameState': self.gameState,
                    'myState': otherPlayer.toJSON(),
                    'opponentState': currentPlayer.toJSON()
                }
            )

    def player_quit(self, socket):
        currentPlayer, otherPlayer = self.whichPlayer(socket)

        # Send message to the other player
        otherPlayer.socket.write_message(json.dumps({
            'command': 'quit'
        }))

         # Delete Game
        self.deleteGame(socket.application)

    def end_game(self, socket):
        currentPlayer, otherPlayer = self.whichPlayer(socket)

        # Check if both games are over
        currentPlayer.isGameOver = True

        if otherPlayer.isGameOver:
            # Send final message

            if currentPlayer.score > otherPlayer.score:

                # If the current player won
                currentPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_WON
                })

                otherPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_LOST
                })
            elif currentPlayer.score < otherPlayer.score:
                # If the current player lost
                otherPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_WON
                })

                currentPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_LOST
                })
            else:
                # If there was a draw
                otherPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_DRAW
                })

                currentPlayer.socket.write_message({
                    'command': constants.FINAL_COMMAND,
                    'outcome': constants.GAME_OUTCOME_DRAW
                })

            if currentPlayer.socket in app.gameLookup:
                del app.gameLookup[currentPlayer.socket]

            if otherPlayer.socket in app.gameLookup:
                del app.gameLookup[otherPlayer.socket]

    def whichPlayer(self, socket):
        # Find which player made the move
        currentPlayer = None
        otherPlayer = None

        if self.player1.socket == socket:
            currentPlayer = self.player1
            otherPlayer = self.player2
        else:
            currentPlayer = self.player2
            otherPlayer = self.player1

        return (currentPlayer, otherPlayer)
