import pickle
import os.path
import datetime
import random
import time
from trello.trelloclient import TrelloClient 
from trello.util import create_oauth_token

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
			roll = random.randrange(1,5) + random.randrange(1,5)
			print("You rolled a {}".format(roll))
			self.move(roll)

	def move(self, roll):
		board_length = len(self.game_state.board)
		new_location = self.game_state.board_location + roll
		if new_location >= board_length:
			self.game_state.credits+=200
			self.game_state.board_location = new_location % board_length
		else:
			self.game_state.board_location = new_location
		print("Board location:{}".format(self.game_state.board_location))
		self.game_state.print_board()
		try:
			self.game_state.board[self.game_state.board_location].function()
		except AttributeError as e:
			print("Error! Function not yet implemented for {}".format(self.game_state.board[self.game_state.board_location]))
			print(e)
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
						"Academic Probation (Just visiting)",
						ChoreProperty("2 Short Chores", 10, self.trello_board),
						HomeworkProperty("Medium HW", 30, self.trello_board),
						CreditsProperty("100 Credits!",100,self),
						CreditsProperty("South Lounge", random.randrange(1,100),self),
						ChoreProperty("Medium Chore", 15, self.trello_board), 
						HomeworkProperty("Long HW", 45, self.trello_board),
						"Go on a Run",
						"Go to Academic Probation", 
						ChoreProperty("Large Chore", 30, self.trello_board),
						HomeworkProperty("Huge HW", 60, self.trello_board),
						"30 Minutes of Work on This!"]

	def print_board(self):
		arrows = ["-->" if x==self.board_location else "   " for x in range(len(self.board))]

		for i in range(len(self.board)):
			print(arrows[i],self.board[i])
		print("Credits:{}".format(self.credits))



class Property:
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return self.name

class CardWithLabelProperty(Property):
	def __init__(self, name, time, board):
		super().__init__(name)
		self.time = time
		self.board = board
		self.activity = ""

	def assignCard(self, card):
		if card is not None:
			print("Time to spend {} minutes on {}!".format(self.time, self.activity))
			print("Spend {} minutes doing '{}' and the come back to roll again!".format(self.time, card.name))
			time.sleep(.01 * self.time)
			while True:
				reply = input("Did you finish the assignment? (y/n): ")
				if (reply=="yes" or reply=="y"):
					card.delete()
					break
				elif(reply=="n" or reply == "no"):
					break

	def getCards(self):
		print(self.label)
		all_cards = self.board.all_cards()
		selected_cards = []
		for card in all_cards:
			for label in card.labels:
				if label.name == self.label:
					selected_cards.append(card)
		return selected_cards

class HomeworkProperty(CardWithLabelProperty):
	def __init__(self,name, time, board):
		super().__init__(name, time, board)
		self.function = self.assignHomework
		self.activity = "homework"
		self.label = "Homework"

	def assignHomework(self):
		homework_cards = self.getCards()
		homework_cards = [card for card in homework_cards if card.due_date!='']
		homework_cards = sorted(homework_cards, key=lambda x: x.due_date)
		self.assignCard(homework_cards[0])

class ChoreProperty(CardWithLabelProperty):
	def __init__(self, name, time, board):
		super().__init__(name, time, board)
		self.function = self.assignChore
		self.activity = "chores"
		self.label = "Chore"

	def assignChore(self):
		chores = self.getCards()
		self.assignCard(random.choice(chores))


class WorkoutProperty(Property):
	def __init__(self, name, time):
		super().__init__(name)
		self.time = time
		self.workouts = ["Core", "Upper Body", "Cardio", "Jump Cardio"]
		self.function = self.doWorkout

	def doWorkout(self):
		print("Time to get some exercise!  Come back once you have spent at least {} minutes doing a {} workout".format(self.time, random.choice(self.workouts)))
		time.sleep(self.time * 60)
		print("Done working out! Time to roll again")

class CreditsProperty(Property):
	def __init__(self, name, amount, state):
		super().__init__(name)
		self.amount = amount
		self.state = state
		self.function = self.changeCredits

	def changeCredits(self):
		self.state.credits += self.amount
		print("Congrats! You got {} credits!".format(self.amount))


if __name__ == '__main__':
	game = Game()
	game.play_game()
