# Game Class
from skyjo.core.errors import InvalidCard
from skyjo.core.player import Player
from skyjo.core.deck import Deck

command_mapping = {
        "db": "draw_from_bin",
        "dd": "draw_from_deck",
        "rc": "replace_card",
        "dc": "discover_card"
    }
class Game:
    def __init__(self, players : list[Player], deck):
        self.players = players
        self.deck = deck
        self.legal_draw = ["draw_from_bin", "draw_from_deck"]
        self.legal_action = ["replace_card", "discover_card"]
        self._distribute_cards()

    def _distribute_cards(self):
        self.deck.shuffle()
        for p in self.players:
            for row in range(0,3):
                for col in range(0,4):
                    card = self.deck.pop_random_card()
                    p._cards[row][col] = card

    def _check_valid_card(self, card_val):
        try: 
            int(card_val)
            return True
        except:
            raise InvalidCard(f"Erreur : la carte {card_val} n'est pas valide")

            
    def _check_legality(self, move, type):
        cmd = command_mapping.get(move, None)
        if cmd is None: return False

        if type == 'draw':
            if cmd not in self.legal_draw: return False
            else: return True
        elif type == "play":
            if cmd not in self.legal_action: return False
            else: return True
    
    def check_current_count(self):
        count = {}
        for p in self.players:
            player_count = 0
            for row in p.cards:
                player_count += sum([i for i in row if isinstance(i, int)])
            count[p.name] = player_count
        return count

    def fetch_bin(self):
        return self.deck.fetch_bin()

    def is_game_over(self):
        for p in self.players:
            if len(p._revealed_cards_map) == 12: return True
        return False

    def draw_from_deck(self, p: Player):
        drawn_card = self.deck.pop_random_card()
        
        accept = ''
        while accept not in ["Y", "y", "N", "n"]:
            accept = input("Keep ? (Y/n)")

        if accept.lower() == "y":
            x = input("Row : ")
            y = input("Column : ")
            prev_card = p.change_card(x, y, drawn_card)
            self.deck.send_to_bin(prev_card)
        
        else:
            print("Reveal :")
            x = input("Row : ")
            y = input("Column : ")
            self.deck.send_to_bin(drawn_card)
            p.reveal_card(x, y)


    def draw_from_bin(self, p: Player):
        card = self.deck.fetch_bin()
        print("Replace :")
        x = input("Row : ")
        y = input("Column : ")
        prev_card = p.change_card(x, y, card)
        self.deck.send_to_bin(prev_card)

