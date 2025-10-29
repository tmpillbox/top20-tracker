from src.modes.mode import ManagerMode
from src.modes.games.cmd_set import CmdGamesMode


from typing import List, Optional


class GamesMode(ManagerMode):
    _cmd_sets = [ CmdGamesMode ]

    def choices_game_name(self) -> List[str]:
        return self.manager.choices_game_name()

    def add_game(self, name: str) -> Optional[bool]:
        return self.manager.add_game(name)

    def delete_game(self, name: str, force: bool = False) -> Optional[bool]:
        return self.manager.delete_game(name, force)

    def _render_games_table(self) -> Optional[bool]:
        return self.manager._render_games_table()

    def _render_one_game(self, game_name: str) -> Optional[bool]:
        return self.manager._render_one_game(game_name)