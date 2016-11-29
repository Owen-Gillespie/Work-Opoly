import pickle
import os.path
import datetime
import random

class Game:

	def __init__(self, name):
		self.credits = 0
		self.last_play = datetime.datetime.now()
		self.name = name
		self.board_location = 0
		self.board_names = ["Home", "1 Small Chore", "15 Minutes of Homework", "10 Minute Workout", "Academic Probation", "2 Small Chores",
								"30 Minute of Homework", "100 Credits", "South Lounge", "1 Medium Chore", "45 Minutes of Homework", "Go On a Run",
								"Go to Academic Probation", "1 Large Chore", "60 Minutes of Homework", "League/Netflix"]
		self.board_functions = [x for x in range(10)]
		self.board_length = 10


def load_game():
	if(os.path.isfile('game_state.p')):
		f = open('game_state.p', "rb")
		global game_state
		game_state = pickle.load(f)
		print("Welcome {}! It has been {} days since you last played.\n You have {} credits!".format(game_state.name, (datetime.datetime.now() - game_state.last_play).days, game_state.credits))
	else:
		print("Welcome to Work-Opoly!")
		name = input("What is your name? ")
		game_state = Game(name)
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
	if new_location > game_state.board_length:
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
	game_state = load_game()
	# save_game(game_state)
	play_game(game_state)
