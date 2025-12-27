
class Player:
    command_mapping = {
    "db": "draw_from_bin",
    "dd": "draw_from_deck",
    "rc": "replace_card",
    "dc": "discover_card"
}

    def __init__(self, name):
        self.cards = [["?", "?", "?", "?"] for _ in range(3)]
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
        self._cards[int(row)][int(col)] = new_card
        self._update_cards_view()
        return prev_card
    
    def show_cards(self):
        return self.cards
            
    def _show_hidden_cards(self):
        return(self._cards)




    

                



    

        






