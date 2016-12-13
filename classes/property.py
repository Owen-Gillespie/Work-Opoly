
class Property:
	def __init__(self, name):
		self.name = name
		self.timer = 0

	def __repr__(self):
		return self.name

	def sleep(self):
		if(self.timer!=0):
			print("Starting {} minute timer".format(self.timer))
			time.sleep(self.timer * 60)
			print("Timer done")



class CardWithLabelProperty(Property):
	def __init__(self, name, time, board):
		super().__init__(name)
		self.timer = time
		self.board = board
		self.activity = ""

	def assignCard(self, card):
		if card is not None:
			print("Time to spend {} minutes on {}!".format(self.timer, self.activity))
			print("Spend {} minutes doing '{}' and the come back to roll again!".format(self.timer, card.name))
			self.sleep()
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

class JailProperty(HomeworkProperty):
	def __init__(self,name, game_state):
		super().__init__(name, 30, game_state.trello_board)
		self.function
		self.state = game_state
		self.turns_left = 3
		self.function = self.inJail

	def inJail(self):
		while self.turns_left > 0:
			while True:
				choice = input("Do you want to try to roll out of AP? (y/n):")
				if choice == "y" or choice == "n":
					break
			if choice == "y":
				roll1 = random.randrange(1,5)
				roll2 = random.randrange(1,5)
				print("You rolled a {} and {}".format(roll1, roll2))
				if roll1 == roll2:
					self.turns_left = 0
					self.state.move(roll1, roll2)
				else:
					self.turns_left -= 1
					self.assignHomework()
			else:
				self.turns_left -= 2
				self.assignHomework()



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
		self.timer = time
		self.workouts = ["Core", "Upper Body", "Cardio", "Jump Cardio"]
		self.function = self.doWorkout

	def doWorkout(self):
		print("Time to get some exercise!  Come back once you have spent at least {} minutes doing a {} workout".format(self.timer, random.choice(self.workouts)))
		self.sleep()

class CreditsProperty(Property):
	def __init__(self, name, amount, state):
		super().__init__(name)
		self.amount = amount
		self.state = state
		self.function = self.changeCredits

	def changeCredits(self):
		self.state.credits += self.amount
		print("Congrats! You got {} credits!".format(self.amount))

class ChillProperty(Property):
	def __init__(self, name, message, timer):
		super().__init__(name)
		self.message = message
		self.timer = timer
		self.function = self.sendMessage

	def sendMessage(self):
		print(self.message)
		self.sleep()

class GoToProperty(Property):
	def __init__(self, name, destName, message, state):
		super().__init__(name)
		self.destName = destName
		self.message = message
		self.state = state
		self.function = self.goToDest


	def goToDest(self):
		print(self.message)
		destIndex = -1
		for index, spot in enumerate(self.state.board):
			if spot.name == self.destName:
				destIndex = index
				break

		if (destIndex != -1):
			self.state.board_location = destIndex
			self.state.land_on_square()
