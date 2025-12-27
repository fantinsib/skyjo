import numpy as np
import random

command_mapping = {
    "db": "draw_from_bin",
    "dd": "draw_from_deck",
    "rc": "replace_card",
    "dc": "discover_card"
}

class PlayerNotFound(Exception):
    pass

class DeckEmpty(Exception):
    pass



class Deck:
    '''
    Simulates a 150 cards deck with :
    - 5 X (-2) cards
    - 15 X (0) cards
    - 10 X (-1 & 1 to 12) cards

    ### Methods : 
    .remove_card(card_value) -> removes a card that has card_value as value from the deck 
    .pop_card(card_value) -> removes a card that has card_value as value from the deck and returns its value
    .send_to_bin(card_value) -> replace the last card of the bin by a card with card_value
    '''

    def __init__(self):
        #Deck generation 
        deck = []
        deck += 5*[-2] + 15*[0] + 10*[-1]
        for i in range(1, 13):
            deck += [i]*10
        self.deck = deck 
        self.bin = "x"

    def remove_card(self, card_val):
        #Use to remove a card by specifying its value - not returning it 
        self.deck.remove(card_val)
    
    def pop_card(self, card_val):
        #Removes a card from the deck and returns it
        self.remove_card(card_val)
        return card_val

    def pop_random_card(self):
        #Pops a random card in the deck 
        return self.deck.pop(np.random.randint(0, len(self.deck)))

    def send_to_bin(self, card_val):
        self.bin = card_val

    def fetch_bin(self):
        return self.bin
    
    def shuffle(self):
        random.shuffle(self.deck)

    def cards_left(self):
        return len(self.deck)


class Player:

    def __init__(self, name):
        self.cards = [["x", "x", "x", "x"] for _ in range(3)]
        self._cards = [["o", "o", "o", "o"] for _ in range(3)]
        self.name = name
        self.is_a_bot = False
        self.num_of_returned_cards = 0
        self.num_of_cards_left = 12
        self._revealed_cards_map = []

    def __repr__(self):
        return f"Player {self.name}"
    
    def _update_cards_view(self):
        #Update the mapping of revealed cards
        for coords in self._revealed_cards_map:
            self.cards[int(coords[0])][int(coords[1])] = self._cards[int(coords[0])][int(coords[1])]

    def reveal_card(self,row , col):
        #appends a new card to the mapping of revealed cards + update the view
        self._revealed_cards_map.append((int(row), int(col)))
        self._update_cards_view()
        self.show_cards()
        return self.cards[int(row)][int(col)]
    
    def change_card(self, row:int, col:int, new_card:int):
        prev_card = self._cards[int(row)][int(col)]
        self.cards[int(row)][int(col)] = new_card
        return prev_card
    
    def show_cards(self):
        print("\n")
        for r in self.cards:
            print(r)
            
    def _show_hidden_cards(self):
        print(self._cards)



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

    def fetch_bin(self):
        return self.deck.fetch_bin()

    def is_game_over(self):
        for p in self.players:
            if len(p._revealed_cards_map) == 12: return True
        return False

    def draw_from_deck(self, p: Player):
        drawn_card = self.deck.pop_random_card()
        print(drawn_card)
        accept = ''
        while accept not in ["Y", "y", "N", "n"]:
            accept = input("Keep ? (Y/n)")

        if accept.lower() == "y":
            print("Replace :")
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




    

                



    

        






