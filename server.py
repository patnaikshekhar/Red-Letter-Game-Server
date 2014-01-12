# Tornado Imports
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.websocket
import tornado.web

from tornado.options import options

# Standard Library Imports
import json

# Import Constants
import constants

from classes.player import Player
from classes.game import Game


class Application(tornado.web.Application):
    """ This is the main class which starts the
        tornado application """

    def __init__(self):

        handlers = [(r'/websocket', GameHandler)]
        debug = options.debug_mode

        # This holds the list of games
        self.games = {}
        self.gameIndex = 0

        # This holds the game lookup table
        self.gameLookup = {}

        # This contains the player which is waiting
        self.waitingPlayer = None

        # Load the dictionary
        self.dictionary = self.load_dictionary()
        tornado.web.Application.__init__(self, handlers, debug=debug)

    def load_dictionary(self):
        """ This function loads the dictionary of words """

        f = open(constants.DICTIONARY_FILE, 'r')
        ret_dict = f.read()
        f.close()

        return ret_dict


class GameHandler(tornado.websocket.WebSocketHandler):

    """ This is the class which implements most of the
        multiplayer game logic """

    def open(self):
        pass

    def on_message(self, message):

        """ This function recieves a message of type
        {'command': 'name', {object}} and accordingly
        sends a message back to the client
        """

        try:
            msg = json.loads(message)

            if not "command" in msg:
                self.write_message(constants.ERROR_INVALID_MESSAGE)
            else:
                command = msg['command']
                if command == constants.JOIN_COMMAND:
                    """ Passed Message {command: 'join', playerName: name}
                        Return Message {'join'} """

                    self.join(msg)

                elif command == constants.SUBMIT_COMMAND:
                    """ Passed Message {command: 'submit', word} """

                    self.submit(msg)

                elif command == constants.END_COMMAND:
                    """ Passed Message {command: 'end'} """

                    self.end_game(msg)

        except Exception, e:
            self.write_message(constants.ERROR_INVALID_MESSAGE)
            raise

    def join(self, message):
        """ This function checks if there is a player waiting
            for a game. If there is then it creates a game and
            sends a message to the two players to start the game """
        # Check if player is waiting
        if self.application.waitingPlayer is not None:

            # Create Game if player is waiting
            # Find starting player and assign cross or knots to player
            player1 = self.application.waitingPlayer
            player2 = Player(message['name'], self)

            # Set the waiting player to none
            self.application.waitingPlayer = None

            # Add Lookup table
            newIndex = self.application.gameIndex
            self.application.gameLookup[player1.socket] = newIndex
            self.application.gameLookup[player2.socket] = newIndex

            # Create Game Object
            game = Game(player1, player2, newIndex)

            # Add Game to list of games
            self.application.games[newIndex] = game

            # Increment Game index
            self.application.gameIndex += 1

            game.start_game()

        else:
            # Make player wait if there is no other player waiting
            newPlayer = Player(message['name'], self)
            self.application.waitingPlayer = newPlayer

    def submit(self, message):
        """ This function validates the word that was sent """

        if self in self.application.gameLookup:
            gameIndex = self.application.gameLookup[self]
            self.application.games[gameIndex].submit(
                message['word'], self.application.dictionary, self)

    def end_game(self, message):
        """ This function is called when the game ends """

        if self in self.application.gameLookup:
            gameIndex = self.application.gameLookup[self]
            self.application.games[gameIndex].end_game(self)

    def on_close(self):
        """ This function handles the case when the socket is closed """

        # Do a reverse lookup and check which game did
        # the player disconnect from
        if self in self.application.gameLookup:
            gameIndex = self.application.gameLookup[self]
            currentGame = self.application.games[gameIndex]

            # Handle the quit event
            currentGame.player_quit(self)
        elif self.application.waitingPlayer is not None:

            # If waiting player exits then remove waiting player.
            if self.application.waitingPlayer.socket == self:
                self.application.waitingPlayer = None


def main():

    """ This function starts the game server """

    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address='')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
