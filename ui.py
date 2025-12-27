# textual_app.py
from __future__ import annotations

from skyjo_main import Game, Deck, Player

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
    }
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
        # Highlight container if active
        if active:
            self.add_class("active")
        else:
            self.remove_class("active")

        # Update name line (add a marker)
        name_widget = self.query_one(f"#pname-{self.player_id}", Static)
        name_widget.update(f"{player.name}{'  ⟵' if active else ''}")

        # Update cards
        for r in range(3):
            for c in range(4):
                btn = self.query_one(f"#card_{self.player_id}-{r}-{c}", Button)

                # Your Player has both `_cards` (truth) and `cards` (view with 'x')
                # We'll display "?" if hidden, else the number.
                view_val = player.cards[r][c]
                if view_val == "x":
                    btn.label = "?"
                else:
                    btn.label = str(view_val)


class Demo(App):
    TITLE = "Skyjo"
    CSS = """
    Screen { padding: 1; }
    #status { border: round $secondary; padding: 1; margin-bottom: 1; }
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

    # ----------------------------
    # Init model + UI state
    # ----------------------------
    def __init__(self):
        super().__init__()

        # Model
        self.players = [Player("A"), Player("B"), Player("C")]
        self.deck = Deck()
        self.game = Game(self.players, self.deck)

        # Make sure bin starts with a real card (if your Deck starts with "x")
        try:
            if not isinstance(self.game.fetch_bin(), int) and self.deck.cards_left() > 0:
                self.deck.send_to_bin(self.deck.pop_random_card())
        except Exception:
            pass

        # UI / turn state
        self.current_player_idx = 0
        self.phase = "choose_draw"  # choose_draw | choose_keep_or_discard | choose_target_replace | choose_target_reveal | choose_target_bin_replace
        self.pending_card: int | None = None

        # Views
        self.player_views: list[PlayerContainer] = []

    # ----------------------------
    # UI layout
    # ----------------------------
    def compose(self) -> ComposeResult:
        yield Header()
        bin_card = self.game.fetch_bin()

        self.status = Static("Ready", id="status")
        yield self.status

        with Horizontal(id="controls"):
            with Horizontal():
                yield Button("Keep", id="keep", classes="btn")
                yield Button("Discard", id="discard", classes="btn")
                yield Button("Next", id="next", classes="btn")

            yield Static("", classes="spacer")

            with Horizontal():
                with Vertical(classes="card_info"):
                    yield Static("Current Bin")
                    yield Button(f"{bin_card}", id="Bin")
                with Vertical(classes="card_info"):
                    yield Static("From Deck")
                    yield Button("?", id="Draw")

        # Build player containers from model (player_id == index => easy mapping)
        self.player_views = [PlayerContainer(p.name, i) for i, p in enumerate(self.players)]

        # Layout: 2 players per row
        with Vertical():
            for i in range(0, len(self.player_views), 2):
                with Horizontal():
                    yield self.player_views[i]
                    if i + 1 < len(self.player_views):
                        yield self.player_views[i + 1]

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_ui()

    # ----------------------------
    # Helpers (safe reveal/replace without print/input)
    # ----------------------------
    def _reveal(self, player: Player, r: int, c: int) -> None:
        if (r, c) not in player._revealed_cards_map:
            player._revealed_cards_map.append((r, c))
        player.cards[r][c] = player._cards[r][c]

    def _replace(self, player: Player, r: int, c: int, new_card: int) -> int:
        old = player._cards[r][c]
        player._cards[r][c] = new_card

        # Keep view coherent
        if (r, c) in player._revealed_cards_map:
            player.cards[r][c] = new_card
        else:
            player.cards[r][c] = "x"
        return old

    def _end_turn(self) -> None:
        self.pending_card = None
        self.phase = "choose_draw"
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    # ----------------------------
    # BINDINGS actions
    # ----------------------------
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

    # ----------------------------
    # Click handling
    # ----------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        # Control buttons
        if bid == "keep":
            if self.phase == "choose_keep_or_discard" and self.pending_card is not None:
                self.phase = "choose_target_replace"
                self.refresh_ui()
            return

        if bid == "discard":
            if self.phase == "choose_keep_or_discard" and self.pending_card is not None:
                # Discard pending to bin immediately, then choose a card to reveal
                self.deck.send_to_bin(self.pending_card)
                self.pending_card = None
                self.phase = "choose_target_reveal"
                self.refresh_ui()
            return

        if bid == "next":
            self._end_turn()
            self.refresh_ui()
            return

        # Card clicks
        if bid.startswith("card_"):
            # id format: card_<playerId>-<r>-<c>
            try:
                payload = bid.removeprefix("card_")
                p_id_str, r_str, c_str = payload.split("-")
                p_id, r, c = int(p_id_str), int(r_str), int(c_str)
            except Exception:
                return

            # Only allow clicking current player's cards
            if p_id != self.current_player_idx:
                return

            player = self.players[p_id]

            # Replace with pending (keep from deck)
            if self.phase == "choose_target_replace" and self.pending_card is not None:
                old = self._replace(player, r, c, self.pending_card)
                self.deck.send_to_bin(old)
                self._end_turn()
                self.refresh_ui()
                return

            # Reveal a card after discard
            if self.phase == "choose_target_reveal":
                self._reveal(player, r, c)
                self._end_turn()
                self.refresh_ui()
                return

            # Take bin card and replace directly
            if self.phase == "choose_target_bin_replace" and self.pending_card is not None:
                # Taking the bin card is equivalent to replacing the bin top with the old card
                old = self._replace(player, r, c, self.pending_card)
                self.deck.send_to_bin(old)
                self._end_turn()
                self.refresh_ui()
                return

    # ----------------------------
    # UI refresh
    # ----------------------------
    def refresh_ui(self) -> None:
        try:
            bin_card = self.game.fetch_bin()
        except Exception:
            bin_card = "?"

        current_name = self.players[self.current_player_idx].name
        self.status.update(
            f"Player: {current_name} | Phase: {self.phase} | Bin: {bin_card} | Pending: {self.pending_card}"
        )

        for i, view in enumerate(self.player_views):
            view.update_from_player(self.players[i], active=(i == self.current_player_idx))


if __name__ == "__main__":
    Demo().run()
