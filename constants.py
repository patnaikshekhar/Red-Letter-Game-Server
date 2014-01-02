from tornado.options import define

import json

# Defines
define("port", default=8888, help="run on the given port", type=int)
define("debug_mode", default=True, help="run server in debug mode", type=bool)

# Error Message
ERROR_INVALID_MESSAGE = json.dumps({'command': 'error',
                                    'error_message': 'Invalid Message'})
ERROR_GAME_NOT_FOUND = json.dumps({'command': 'error',
                                   'error_message': 'Game not found'})

# This is a list of game outcomes
GAME_OUTCOME_WON = 'won'
GAME_OUTCOME_LOST = 'lost'
GAME_OUTCOME_DRAW = 'draw'

# This is a list of validation outcomes
VALIDATION_OUTCOME_RIGHT = 'right'
VALIDATION_OUTCOME_WRONG = 'wrong'
VALIDATION_OUTCOME_EXISTING = 'existing'

ROW_TILES = 5
COLUMN_TILES = 5

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
           'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
           'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
           'Y', 'Z']

# This is the strength of the tiles which determines the score
STRENGTH_0 = 0
STRENGTH_1 = 1
STRENGTH_2 = 2
STRENGTH_3 = 3
STRENGTH_4 = 4

# These constants store the usage tiers
USAGE_TIER_0 = -2
USAGE_TIER_1 = -4
USAGE_TIER_2 = -6
USAGE_TIER_3 = -8
USAGE_TIER_4 = -10

DICTIONARY_FILE = 'dictionary.json'

# Indicates that an error occurred. This is from Server -> Client
ERROR_COMMAND = 'error'

# Indicate that the game has started. This is from Server -> Client
START_COMMAND = 'start'

# Submit a word to the server. This is from Client -> Server
SUBMIT_COMMAND = 'submit'

# Validates a word and sends true if valid Server -> Client
VALIDATED_COMMAND = 'validated'

# Indicates when the game state has changed Server -> Client
UPDATE_COMMAND = 'update'

# Indicates that a client wants to join the game Client -> Server
JOIN_COMMAND = 'join'

# Indicates that the game has ended Client -> Server
END_COMMAND = 'end'

# Indicates that both the players are finished with the game Server -> Client
FINAL_COMMAND = 'final'

# Indicates that both one of the players left the game -> Client
QUIT_COMMAND = 'quit'
