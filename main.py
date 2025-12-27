import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from skyjo.core.deck import Deck
from skyjo.core.game import Game
from skyjo.core.player import Player
from skyjo.ui.playercontainer import PlayerContainer
from skyjo.ui.app import Skyjo


if __name__ == "__main__":
    Skyjo().run()
