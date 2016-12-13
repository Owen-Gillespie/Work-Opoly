import pickle
import os.path
import datetime
import random
import time
from trello.trelloclient import TrelloClient 
from trello.util import create_oauth_token
from classes.property import CreditsProperty, ChoreProperty, HomeworkProperty, WorkoutProperty, ChillProperty, JailProperty, GoToProperty

class Game:

	def __init__(self):
		self.client = self.create_client()
		self.game_state = self.create_game_state(self.client)

	def create_client(self):
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
			pickle.dump(auth_token, open("trello_oauth_token.p", "wb"))
			auth_token = create_oauth_token(expiration="never", scope="read,write", key=key, secret=secret, name="Work-opoly")
		client = TrelloClient(
		    api_key=key,
		    api_secret=secret,
		    token=auth_token['oauth_token'],
		    token_secret=auth_token['oauth_token_secret']
		)
		return client

	def create_game_state(self, client):
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

			game_state = GameState(name, client, boards[selection - 1])
		return game_state

	def save_game(self):
		pickle.dump(self.game_state, open( "game_state.p","wb") )

	def play_game(self):
		while True:
			player_input = input("Press enter to roll the dice or q to quit")
			if (player_input=="q"):
				self.save_game()
				break
			if (player_input == ""):
				print("moving")
				self.game_state.move()


class GameState:

	def __init__(self, name, trello_client, trello_board):
		self.credits = 0
		self.trello_client = trello_client
		self.trello_board = trello_board
		self.last_play = datetime.datetime.now()
		self.name = name
		self.board_location = 0
		self.board = [CreditsProperty("Shower Suite", 200,self),
						ChoreProperty("Short Chore", 5, self.trello_board),
						HomeworkProperty("Short HW", 15, self.trello_board),
						WorkoutProperty("Short Workout",10),
						JailProperty("Academic Probation", self),
						ChoreProperty("2 Short Chores", 10, self.trello_board),
						HomeworkProperty("Medium HW", 30, self.trello_board),
						CreditsProperty("100 Credits!",100,self),
						CreditsProperty("South Lounge", random.randrange(1,100),self),
						ChoreProperty("Medium Chore", 15, self.trello_board), 
						HomeworkProperty("Long HW", 45, self.trello_board),
						ChillProperty("Take a Run", "Go out for a run, and come back in at least 20 minutes!", 20),
						GoToProperty("Go to Academic Probation", "Academic Probation", "You've been a very naughty student", self), 
						ChoreProperty("Large Chore", 30, self.trello_board),
						HomeworkProperty("Huge HW", 60, self.trello_board),
						ChillProperty("Work on Work-Opoly!", "Think of the functions you wish you had", 30)]

	def print_board(self):
		arrows = ["-->" if x==self.board_location else "   " for x in range(len(self.board))]

		for i in range(len(self.board)):
			print(arrows[i],self.board[i])
		print("Credits:{}".format(self.credits))

	def move_piece(self, distance):
		board_length = len(self.board)
		new_location = self.board_location + distance
		if new_location >= board_length:
			self.credits+=200
			self.board_location = new_location % board_length
		else:
			self.board_location = new_location

	def land_on_square(self):
		self.board[self.board_location].function()

	def move(self, roll1=None, roll2 = None):
		if roll1 == None:
			roll1 = random.randrange(1,5)
		if roll2 == None:
			roll2 = random.randrange(1,5)
	
		print("You rolled a {} and a {} for a total of {}".format(roll1, roll2, roll1 + roll2))
		self.move_piece(roll1 + roll2)
		self.print_board()
		self.land_on_square()


if __name__ == '__main__':
	game = Game()
	game.play_game()
