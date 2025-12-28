#PlayerContainer

from __future__ import annotations

from skyjo.core.deck import Deck
from skyjo.core.game import Game
from skyjo.core.player import Player

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static


class PlayerContainer(Vertical):
    DEFAULT_CSS = """
    /* Conteneur joueur */
    PlayerContainer {
        border: round $secondary;
        padding: 1;
        margin-right: 2;
        margin-bottom: 1;
    }

    PlayerContainer.active {
        border: round $accent;
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
        width: 6;
        height: 3;
        padding: 0;
        margin: 0 1;
        content-align: center middle;
        background: #555555;
    }

    .card.revealed {
        background: #2d74da;
    }

    .card.low { background: #1f5f2a; }
    .card.mid { background: #7b6a1f; }
    .card.high { background: #6b2323; }
    .card.completed { background: #000000;}
    """

    def __init__(self, player_name: str, player_id: int):
        super().__init__()
        self.player_name = player_name
        self.player_id = player_id

    def compose(self) -> ComposeResult:
        yield Static(self.player_name, id=f"pname-{self.player_id}")

        for r in range(3):
            with Horizontal(classes="row"):
                for c in range(4):
                    yield Button(
                        "?",
                        id=f"card_{self.player_id}-{r}-{c}",
                        classes="card",
                    )

    def update_from_player(self, player: Player, active: bool) -> None:
        
        if active:
            self.add_class("active")
        else:
            self.remove_class("active")

        
        name_widget = self.query_one(f"#pname-{self.player_id}", Static)
        revealed_total = 0
        for row in player.cards:
            for val in row:
                if isinstance(val, int):
                    revealed_total += val
        name_widget.update(f"{player.name} ({revealed_total}){'  ⟵' if active else ''}")

        for r in range(3):
            for c in range(4):
                btn = self.query_one(f"#card_{self.player_id}-{r}-{c}", Button)

                view_val = player.cards[r][c]
                if isinstance(view_val, int) or (view_val=="X"):
                    btn.label = str(view_val)
                    btn.remove_class("low", "mid", "high")
                    if btn.label in ["-2","-1","0","1","2","3"]:
                        btn.add_class("low")
                    elif btn.label in ['4','5',"6",'7',"8","9"]:
                        btn.add_class("mid")
                    elif btn.label in ['10','11',"12"]:
                        btn.add_class("high")
                    elif btn.label == "X":
                        btn.add_class("completed")
                    btn.add_class("revealed")
                else:
                    btn.label = "?"
                    btn.remove_class("revealed", "low", "mid", "high")
