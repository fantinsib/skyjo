from skyjo_main import Deck, Player, Game
from game_loop import GameLoop
game_is_on = True

A = Player("A")
B = Player("B")
C = Player("C")

deck = Deck()

players = [A, B, C]

gameloop = GameLoop(Game(players, deck))
gameloop.start()



