import random
import numpy as np


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

    command_mapping = {
    "db": "draw_from_bin",
    "dd": "draw_from_deck",
    "rc": "replace_card",
    "dc": "discover_card"
    }

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

