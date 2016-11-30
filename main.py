import pickle
import os.path
import datetime
import random
from trello.trelloclient import TrelloClient 
from trello.util import create_oauth_token

class Game:

	def __init__(self, name, trello_client, trello_board):
		self.credits = 0
		self.trello_client = trello_client
		self.trello_board = trello_board
		self.last_play = datetime.datetime.now()
		self.name = name
		self.board_location = 0
		self.board_names = ["Home", "1 Small Chore", "15 Minutes of Homework", "10 Minute Workout", "Academic Probation", "2 Small Chores",
								"30 Minute of Homework", "100 Credits", "South Lounge", "1 Medium Chore", "45 Minutes of Homework", "Go on a Run",
								"Go to Academic Probation", "1 Large Chore", "60 Minutes of Homework", "30 Minutes of Work on This!"]
		self.board_length = len(self.board_names)
		self.board_functions = [x for x in range(self.board_length)]


def load_game(client):
	if(os.path.isfile('game_state.p')):
		f = open('game_state.p', "rb")
		global game_state
		game_state = pickle.load(f)
		print("Welcome {}! It has been {} days since you last played.\n You have {} credits!".format(game_state.name, (datetime.datetime.now() - game_state.last_play).days, game_state.credits))
	else:
		print("Welcome to Work-Opoly!")
		name = input("What is your name? ")
		boards = client.list_boards()
		print("I found the following boards on Trello:")
		i = 1
		for board in boards:
			print("{}: {}".format(i, board.name))
			i+=1

		while True:
			selection = input("Please enter the number for the board you would like to use")
			try:
				selection = int(selection)
				if 0 < selection <= i:
					break
				else:
					print("Please choose a valid number")
			except ValueError:
				print("That's not a number!")

		game_state = Game(name, client, boards[selection - 1])
	return game_state

def save_game(game_state):
	pickle.dump(game_state, open( "game_state.p","wb") )

def play_game(game_state):
	while True:
		player_input = input("Press enter to roll the dice or q to quit")
		if (player_input=="q"):
			save_game(game_state)
			break
		roll = random.randrange(1,5) + random.randrange(1,5)
		print("You rolled a {}".format(roll))
		move(game_state, roll)

def move(game_state, roll):
	new_location = game_state.board_location + roll
	if new_location >= game_state.board_length:
		game_state.credits+=200
		game_state.board_location = new_location % game_state.board_length
	else:
		game_state.board_location = new_location
	print("Board location:{}".format(game_state.board_location))
	print_board(game_state)
	# game_state = game_state.board[game_state.board_location](game_state)

def print_board(game_state):
	arrows = ["-->" if x==game_state.board_location else "   " for x in range(game_state.board_length)]

	for i in range(game_state.board_length):
		print(arrows[i],game_state.board_names[i])
	print("Credits:{}".format(game_state.credits))


if __name__ == '__main__':
	f= open("trello_key.txt") #TODO: Move this to the load game func or some sort of init func
	key = f.read()
	f.close()
	f = open("trello_secret.txt")
	secret = f.read()
	f.close()

	if(os.path.isfile('trello_oauth_token.p')):
		f= open("trello_oauth_token.p", "rb")
		auth_token = pickle.load(f)
		f.close()
	else:
		auth_token = create_oauth_token(expiration="never", scope="read,write", key=key, secret=secret, name="Work-opoly")
		pickle.dump(auth_token, open("trello_oauth_token.p", "wb"))
	client = TrelloClient(
	    api_key=key,
	    api_secret=secret,
	    token=auth_token['oauth_token'],
	    token_secret=auth_token['oauth_token_secret']
	)
	game_state = load_game(client)
	save_game(game_state)
	play_game(game_state)
