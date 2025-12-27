import sys
print("Importing classes...")
from skyjo_main import  Deck, Game,Player
command_mapping = {
    "db": "draw_from_bin",
    "dd": "draw_from_deck",
    "rc": "replace_card",
    "dc": "discover_card"
}

class GameLoop:
    def __init__(self, game: Game):
        self.game = game
        self.game_is_over = False

    def start(self):
        while self.game_is_over == False:
            for p in self.game.players:
                self.players_turn(p)
                print(self.game.is_game_over())
                self.game_is_over = self.game.is_game_over()

    def players_turn(self, p):
        player_index = self.game.players.index(p)
        print("Player : ", p)
        print(command_mapping)
        is_legal_move = False
        print(f"Current card in bin : {self.game.fetch_bin()}")
        print("Your current cards :")
        p.show_cards()
        while is_legal_move == False:
            print("Your turn :")
            draw_type = input("Your turn - enter command : ")
            is_legal_move = self.game._check_legality(draw_type, "draw")
        if draw_type == "db": self.game.draw_from_bin(self.game.players[player_index])
        if draw_type == "dd": self.game.draw_from_deck(self.game.players[player_index])
        self.game.players[player_index].show_cards()
        print("-"*50)
        print("\n"*2)
        
        

