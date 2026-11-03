from src.models.results.result_game import ResultGame
from src.models.votes.vote_game import VoteGame


from rich.console import Console


from typing import TYPE_CHECKING, Dict, List, Optional, Union


if TYPE_CHECKING:
    from src.tracker_manager import TrackerManager

class ManagerMode:
    _cmd_sets = []

    def __init__(self, name: str, manager: "TrackerManager", context: List[str], env: Dict[str, Union[int, str]]):
        self.name: str = name
        self._mode_cmd_sets = list()
        for cmd_set in self._cmd_sets:
            self._mode_cmd_sets.append(cmd_set(self))
        self.manager: "TrackerManager" = manager
        self.context: List[str] = [ ctx for ctx in context ]
        self.env: Dict[str, Union[int, str]] = { k: v for k, v in env.items() }

    def __str__(self) -> str:
        if self.context:
            ctx = ' | ' + ' | '.join(self.context)
        else:
            ctx = ''
        return f' {self.name}{ctx}'

    @property
    def console(self) -> Console:
        return self.manager.console

    def confirm(self, message: str, default: bool = False) -> Optional[bool]:
        return self.manager.confirm(message, default)

    def perror(self, *args, **kwargs) -> None:
        return self.manager.perror(*args, **kwargs)

    def pwarning(self, *args, **kwargs) -> None:
        return self.manager.pwarning(*args, **kwargs)

    def poutput(self, *args, **kwargs) -> None:
        return self.manager.poutput(*args, **kwargs)

    def do_help(self, *args, **kwargs) -> Optional[bool]:
        return self.manager.do_help(*args, **kwargs)

    @property
    def year(self) -> int:
        return self.manager.year

    def _post_init(self) -> None:
        pass

    def setup(self, callback_fn=None) -> None:
        for cmd_set in self._mode_cmd_sets:
            self.manager.register_command_set(cmd_set)
        if callable(callback_fn):
            callback_fn(self, self.manager)

    def teardown(self, callback_fn=None) -> None:
        for cmd_set in self._mode_cmd_sets:
            self.manager.unregister_command_set(cmd_set)
        if callable(callback_fn):
            callback_fn(self, self.manager)

    def _game_by_vote(self, rank: str) -> Optional["VoteGame"]:
        return self.manager._game_by_vote(rank)

    def _vote_by_name(self, game: str) -> Optional[str]:
        return self.manager._vote_by_game(game)

    def _render_votes_table(self) -> Optional[bool]:
        return self.manager._render_votes_table()

    def choices_game_name(self) -> List[str]:
        return self.manager.choices_game_name()

    def set_vote(self, year: int, vote: str, game: str) -> Optional[bool]:
        return self.manager.set_vote(year, vote, game)

    def delete_vote(self, year: int, vote: str, game: str, force: bool) -> Optional[bool]:
        return self.manager.delete_vote(year, vote, game, force)

    def result_by_name(self, game_name: str) -> Optional["ResultGame"]:
        return self.manager.result_by_name(game_name)
    
    def rank_by_result(self, result: "ResultGame") -> Union[str, int]:
        return self.manager.rank_by_result(result)
