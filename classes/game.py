# Standard Library Imports
import json
import random

# Import constants
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

        for row in xrange(constants.ROW_TILES):

            row_list = []

            for col in xrange(constants.COLUMN_TILES):

                random_letter = random.choice(constants.LETTERS)
                gameLetterUsage[random_letter] = 0
                gameLetterStrength[random_letter] = constants.STRENGTH_0

                row_list.append(random_letter)

            gameLetterGrid.append(row_list)

        self.gameState['grid'] = gameLetterGrid
        self.gameState['usage'] = gameLetterUsage
        self.gameState['strength'] = gameLetterStrength

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
            'command': constants.START_COMMAND,
            'myState': self.player1.toJSON(),
            'opponentState': self.player2.toJSON(),
            'gameState': self.gameState
        }))

        self.player2.socket.write_message(json.dumps({
            'command': constants.START_COMMAND,
            'opponentState': self.player1.toJSON(),
            'myState': self.player2.toJSON(),
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

        if validation_result == constants.VALIDATION_OUTCOME_RIGHT:
            # Update Game State
            self.update_game_state(currentPlayer, word)

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

        # Send validation result
        validation_msg = {
            'command': constants.VALIDATED_COMMAND,
            'result': validation_result
        }

        currentPlayer.socket.write_message(validation_msg)

    def player_quit(self, socket):
        currentPlayer, otherPlayer = self.whichPlayer(socket)

        # Send message to the other player
        otherPlayer.socket.write_message(json.dumps({
            'command': constants.QUIT_COMMAND
        }))

         # Delete Game
        self.delete_game(socket.application)

    def end_game(self, socket):
        currentPlayer, otherPlayer = self.whichPlayer(socket)

        def final_message(player, outcome):

            currentPlayer, otherPlayer = self.whichPlayer(player.socket)

            currentPlayer.socket.write_message({
                'command': constants.FINAL_COMMAND,
                'outcome': outcome,
                'myState': currentPlayer.toJSON(),
                'opponentState': otherPlayer.toJSON()
            })

        # Check if both games are over
        currentPlayer.isGameOver = True

        if otherPlayer.isGameOver:
            # Send final message

            if currentPlayer.score > otherPlayer.score:
                # If the current player won
                final_message(currentPlayer, constants.GAME_OUTCOME_WON)
                final_message(otherPlayer, constants.GAME_OUTCOME_LOST)
            elif currentPlayer.score < otherPlayer.score:
                # If the current player lost
                final_message(otherPlayer, constants.GAME_OUTCOME_WON)
                final_message(currentPlayer, constants.GAME_OUTCOME_LOST)
            else:
                # If there was a draw
                final_message(currentPlayer, constants.GAME_OUTCOME_DRAW)
                final_message(otherPlayer, constants.GAME_OUTCOME_DRAW)

            # Delete game once done
            self.delete_game(currentPlayer.socket.application)

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

    def update_game_state(self, currentPlayer, word):
        """ This function updates the game state """

        # Calculate the new score
        score = self.calculate_score(word)
        currentPlayer.score += score

        # Update the usage
        self.update_usage(word)

        # Update the strength
        self.update_strength()

        word = {
            'word': word,
            'score': score
        }

        currentPlayer.wordList.append(word)

    def calculate_score(self, word):
        """ This function calculates the strength of the word made """

        strength = 1
        for char in word:
            strength *= (self.gameState['strength'][char] + 1)

        return (len(word) * strength)

    def update_usage(self, word):
        """ This function updates the usage of the game state """

        for letter in self.gameState['usage']:
            if letter not in word:
                self.gameState['usage'][letter] -= 1
            else:
                self.gameState['usage'][letter] += 1

    def update_strength(self):
        # This function updates the strength
        for letter in self.gameState['usage']:

            usage = self.gameState['usage'][letter]

            if usage >= constants.USAGE_TIER_0:
                self.gameState['strength'][letter] = constants.STRENGTH_0
            elif (usage < constants.USAGE_TIER_0 and
                  usage >= constants.USAGE_TIER_1):
                self.gameState['strength'][letter] = constants.STRENGTH_1
            elif (usage < constants.USAGE_TIER_1 and
                  usage >= constants.USAGE_TIER_2):
                self.gameState['strength'][letter] = constants.STRENGTH_2
            elif (usage < constants.USAGE_TIER_2 and
                  usage >= constants.USAGE_TIER_3):
                self.gameState['strength'][letter] = constants.STRENGTH_3
            else:
                self.gameState['strength'][letter] = constants.STRENGTH_4

    def delete_game(self, app):
        # Remove Game from the list of games and the game lookup
        if self.gameIndex in app.games:
            del app.games[self.gameIndex]

        if self.player1.socket in app.gameLookup:
            del app.gameLookup[self.player1.socket]

        if self.player2.socket in app.gameLookup:
            del app.gameLookup[self.player2.socket]
