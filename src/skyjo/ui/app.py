# textual_app.py
from __future__ import annotations

from skyjo.core.deck import Deck
from skyjo.core.game import Game
from skyjo.core.player import Player
from skyjo.ui.playercontainer import PlayerContainer


from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static


class Skyjo(App):
    TITLE = "Skyjo"
    CSS = """
    Screen { padding: 1; }
    #turn_header { border: round $secondary; padding: 1; margin-bottom: 1; content-align: center middle; text-style: bold; }
    #controls { height: auto; border: round $secondary; padding: 1; margin-bottom: 1; }
    #controls > Horizontal { height: auto; }
    #controls Vertical { height: auto; }
    .btn { margin-right: 1; }
    .spacer { width: 1fr; height: 1; }
    .card_info { width: auto; height: auto; margin-left: 1; }
    #Draw { background: $success 20%; }
    #Bin { background: $error 20%; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "draw_deck", "Deck"),
        ("b", "draw_bin", "Bin"),
    ]


    def __init__(self):
        super().__init__()

        
        self.players = [Player("A"), Player("B")]
        self.deck = Deck()
        self.game = Game(self.players, self.deck)

        try:
            if not isinstance(self.game.fetch_bin(), int) and self.deck.cards_left() > 0:
                self.deck.send_to_bin(self.deck.pop_random_card())
        except Exception:
            pass

      
        self.current_player_idx = 0
        self.phase = "choose_draw"  
        self.pending_card: int | None = None

        self.player_views: list[PlayerContainer] = []

    def compose(self) -> ComposeResult:
        bin_card = self.game.fetch_bin()

        self.turn_header = Static("", id="turn_header")
        yield self.turn_header

        with Horizontal(id="controls"):
            with Horizontal():
                with Vertical(classes="card_info"):
                    yield Static("Current Bin")
                    yield Button(f"{bin_card}", id="Bin")
                with Vertical(classes="card_info"):
                    yield Static("From Deck")
                    yield Button("?", id="Draw")

            yield Static("", classes="spacer")

            with Horizontal():
                yield Button("Keep", id="keep", classes="btn")
                yield Button("Discard", id="discard", classes="btn")

        self.player_views = [PlayerContainer(p.name, i) for i, p in enumerate(self.players)]

        with Vertical():
            for i in range(0, len(self.player_views), 2):
                with Horizontal():
                    yield self.player_views[i]
                    if i + 1 < len(self.player_views):
                        yield self.player_views[i + 1]

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_ui()

    def _reveal(self, player: Player, r: int, c: int) -> None:
        if (r, c) not in player._revealed_cards_map:
            player._revealed_cards_map.append((r, c))
        player.cards[r][c] = player._cards[r][c]

    def _replace(self, player: Player, r: int, c: int, new_card: int) -> int:
        old = player._cards[r][c]
        player._cards[r][c] = new_card
        if (r, c) not in player._revealed_cards_map:
            player._revealed_cards_map.append((r, c))
        player.cards[r][c] = new_card
        return old

    def _end_turn(self) -> None:
        self.pending_card = None
        self.phase = "choose_draw"
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)



    def action_draw_deck(self) -> None:
        if self.phase != "choose_draw":
            return
        if self.deck.cards_left() <= 0:
            return

        self.pending_card = self.deck.pop_random_card()
        self.phase = "choose_keep_or_discard"
        self.refresh_ui()

    def action_draw_bin(self) -> None:
        if self.phase != "choose_draw":
            return

        bin_card = self.game.fetch_bin()
        if not isinstance(bin_card, int):
            return

        self.pending_card = bin_card
        self.phase = "choose_target_bin_replace"
        self.refresh_ui()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        if bid == "Draw":
            self.action_draw_deck()
            return

        if bid == "Bin":
            self.action_draw_bin()
            return

        if bid == "keep":
            if self.phase == "choose_keep_or_discard" and self.pending_card is not None:
                self.phase = "choose_target_replace"
                self.refresh_ui()
            return

        if bid == "discard":
            if self.phase == "choose_keep_or_discard" and self.pending_card is not None:
                self.deck.send_to_bin(self.pending_card)
                self.pending_card = None
                self.phase = "choose_target_reveal"
                self.refresh_ui()
            return

        if bid.startswith("card_"):
            # id format: card_<playerId>-<r>-<c>
            try:
                payload = bid.removeprefix("card_")
                p_id_str, r_str, c_str = payload.split("-")
                p_id, r, c = int(p_id_str), int(r_str), int(c_str)
            except Exception:
                return

            if p_id != self.current_player_idx:
                return

            player = self.players[p_id]

            if self.pending_card is not None and self.phase in (
                "choose_target_replace",
                "choose_keep_or_discard",
            ):
                old = self._replace(player, r, c, self.pending_card)
                self.deck.send_to_bin(old)
                self._end_turn()
                self.refresh_ui()
                return

            if self.phase == "choose_target_reveal":
                self._reveal(player, r, c)
                self._end_turn()
                self.refresh_ui()
                return
            
            if self.phase == "choose_target_bin_replace" and self.pending_card is not None:
                old = self._replace(player, r, c, self.pending_card)
                self.deck.send_to_bin(old)
                self._end_turn()
                self.refresh_ui()
                return


    def refresh_ui(self) -> None:
        try:
            bin_card = self.game.fetch_bin()
        except Exception:
            bin_card = "?"

        bin_btn = self.query_one("#Bin", Button)
        if isinstance(bin_card, int):
            bin_btn.label = str(bin_card)
        else:
            bin_btn.label = "?"

        draw_btn = self.query_one("#Draw", Button)
        if self.phase == "choose_keep_or_discard" and self.pending_card is not None:
            draw_btn.label = str(self.pending_card)
        else:
            draw_btn.label = "?"

        phase_instructions = {
            "choose_draw": "Pioche: deck ou bin",
            "choose_keep_or_discard": "Garder ou defausser la carte",
            "choose_target_replace": "Choisis une carte a remplacer",
            "choose_target_reveal": "Choisis une carte a reveler",
            "choose_target_bin_replace": "Choisis une carte a remplacer (bin)",
        }

        current_name = self.players[self.current_player_idx].name
        instruction = phase_instructions.get(self.phase, "")
        self.turn_header.update(f"{current_name} - {instruction}".strip())

        for i, view in enumerate(self.player_views):
            view.update_from_player(self.players[i], active=(i == self.current_player_idx))


