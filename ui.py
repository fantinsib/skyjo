# textual_app.py
from __future__ import annotations
from skyjo_main import Game, Deck, Player
from game_loop import GameLoop

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static


class Demo(App):

    TITLE = "Skyjo"
    CSS = """
    Screen {
        padding: 1;
    }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "draw_deck", "Deck"),
        ("b", "draw_bin", "Bin"),
    ]

    def on_mount(self):
        game_is_on = True

        A = Player("A")
        B = Player("B")
        C = Player("C")
        self.players = [A, B, C]
        self.deck = Deck()
        self.game = Game(self.players, self.deck)

        
        self.player1 = PlayerContainer("John", 1)
        self.player2 = PlayerContainer("Jack", 2)
        self.player3 = PlayerContainer("Jeff", 3)
        
        players_view = [self.player1,self.player2,self.player3, self.player4]

        

    def compose(self) -> ComposeResult:
        self.header = Header()
        yield self.header

        self.footer = Footer()
        yield self.footer
        
        self.label = Static("Hello")
        yield self.label
        yield Button("Click")


        with Vertical():
            for i in range(0, len(players_list), 2):
                with Horizontal():
                    yield players_list[i]
                    if i + 1 < len(players_list):
                        yield players_list[i + 1]
                        
 

    def refresh_ui(self):
        

class PlayerContainer(Vertical):

    DEFAULT_CSS = """
    /* Conteneur joueur */
    PlayerContainer {
        border: round $secondary;
        padding: 1;
        margin-right: 2;
    }

    /* Nom du joueur */
    PlayerContainer > Static {
        margin-bottom: 1;
        content-align: center middle;
        text-style: bold;
    }

    /* Ligne de cartes */
    .row {
        height: auto;
        margin: 0;
    }

    /* Carte */
    .card {
        width: 2;
        height: 7;
        padding: 0;
        margin: 0 1;
        content-align: center middle;
    }
    """

    def __init__(self, player_name: str, player_id: int):
        super().__init__()
        self.player_name = player_name
        self.player_id = player_id

    def compose(self):
        yield Static(self.player_name)
        
        for r in range(3):
            with Horizontal(classes="row"):
                for c in range(4):
                    yield Button(
                        "?",
                        id=f"card_{self.player_id}-{r}-{c}",
                        classes='card'
                    )

    

Demo().run()
