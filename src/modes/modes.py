import argparse
from src.ResultGame import ResultGame
from src.ResultYear import ResultYear
from rich.table import Table
from src.VoteGame import VoteGame


from rich.console import Console


from typing import TYPE_CHECKING, Dict, List, Optional, Union

from src.modes.mode_commands import CmdGamesMode, CmdGroupingsMode, CmdResultsMode, CmdVotesMode

if TYPE_CHECKING:
    from src.TrackerManager import TrackerManager

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


class ResultsMode(ManagerMode):
    _cmd_sets = [ CmdResultsMode ]

    def _choices_grouped_items(self) -> List[str]:
        rank = self._get_context_rank()
        if rank is None:
            return list()
        return self.manager._choices_grouped_items(str(rank))

    def _choices_selected_grouped_items(self) -> List[str]:
        rank = self._get_context_rank()
        if rank is None:
            return list()
        return self.manager._choices_selected_grouped_items(str(rank))

    def _choices_import_result_items(self, year: Optional[Union[int, str]] = None) -> List[str]:
        return self.manager._all_result_games(year)

    def _choices_result_years(self) -> List[int]:
        return [ year for year in self.manager._results.years ]

    def _results_select(self, rank: int) -> None:
        self.context = [ str(rank) ]
        self.manager._update_prompt()

    def _results_clear(self) -> None:
        self.context = [ ]
        self.manager._update_prompt()

    def _results_next(self) -> None:
        curr_rank = int(self.context[-1])
        self.context = [ str(curr_rank - 1) ]
        self.manager._update_prompt()

    def _get_context_rank(self) -> Optional[int]:
        if not self.context:
            return None
        try:
            return int(self.context[0])
        except:
            return None
        return None

    def _results_show(self) -> None:
        rank = self._get_context_rank()

        if rank is None:
            return
        year = self.manager._results.year(self.manager.year)
        if year is None:
            return
        result = year.by_rank(rank)
        if result is None:
            self.manager.poutput('Not Found')
            return
        table = Table(title=result.name)
        table.show_header = False
        table.add_column('')
        table.add_column('')

        table.add_row('OWN', 'Yes' if result.own else 'No')
        table.add_row('PREV_OWNED', 'Yes' if result.prev_owned else 'No')
        table.add_row('WISHLIST', result.wishlist)
        table.add_row('PLAYED', 'Yes' if result.played else 'No')
        table.add_row('OWNED ITEMS', '\n'.join(result.owned_items))

        self.manager.console.print(table)

    def _render_results(self, ns: argparse.Namespace) -> None:
        return self.manager._render_results(ns)

    def get_result(self, rank: int) -> Optional["ResultGame"]:
        year: Optional[ResultYear] = self.manager._results.year(self.year)
        while year is None:
            self.manager._results.add_year(self.year)
            year = self.manager._results.year(self.year)
        return year.by_rank(rank)

    def _pre_mark(self) -> Optional["ResultGame"]:
        rank = self._get_context_rank()
        if rank is None:
            self.perror('results: must select rank before you can mark')
            return None
        result: Optional[ResultGame] = self.get_result(rank)
        if result is None:
            self.perror('results: must set result game before you can mark')
            return None
        return result

    def _mark_own(self, val: bool) -> Optional[bool]:
        result = self._pre_mark()
        if result is not None:
            result.own = val
            return
        return False

    def _mark_prev_owned(self, val: bool) -> Optional[bool]:
        result = self._pre_mark()
        if result is not None:
            result.prev_owned = val
            return
        return False

    def _mark_wishlist(self, val: str) -> Optional[bool]:
        result = self._pre_mark()
        if result is not None:
            result.wishlist = val
            return
        return False

    def _mark_played(self, val: bool) -> Optional[bool]:
        result = self._pre_mark()
        if result is not None:
            result.played = val
            return
        return False

    def _mark_owned_items(self, action: str, game: str) -> Optional[bool]:
        result = self._pre_mark()
        if result is None:
            return False
        match action:
            case 'add':
                if game not in result.owned_items:
                    result.owned_items.append(game)
            case 'remove':
                if game in result.owned_items:
                    result.owned_items.remove(game)

    def set_add(self, game_name: str) -> Optional[bool]:
        # year = self.manager._results.year(self.year)
        # while year is None:
        #     self.manager._results.add_year(self.year)
        #     year = self.manager._results.year(self.year)
        rank = self._get_context_rank()
        if rank is None:
            self.perror('results: must select a result ranking before adding a game')
            return False
        self.manager._results.add_result(self.year, rank, ResultGame(game_name))

    def set_import(self, game_name: str, year: Optional[int] = None):
        if year is None:
            # Find most recent year other before current year
            year = max([ y for y in self.manager._results.years.keys() if y < self.year ])
        target_year = self.manager._results.year(year)
        if target_year is None:
            self.perror('results: this can\'t happen. Have a nice day.')
            return False
        target_game = target_year.by_name(game_name)
        if target_game is None:
            self.perror(f'results: cannot find {game_name} in results year {year}')
            return False
        rank = self._get_context_rank()
        if rank is None:
            self.perror('results: must select a result ranking before adding a game')
            return False
        self.manager._results.add_result(
            self.year,
            rank,
            ResultGame.from_dict(target_game.as_dict)
        )


class VotesMode(ManagerMode):
    _cmd_sets = [ CmdVotesMode ]


class GroupingsMode(ManagerMode):
    _cmd_sets = [ CmdGroupingsMode ]

    def choices_groupings_name(self) -> List[str]:
        return self.manager.choices_groupings_name()

    def _render_groupings_table(self) -> None:
        if self.manager._groupings is None:
            return
        table = Table(title='Groupings')
        table.add_column('# Entries')
        table.add_column('Grouping')
        groupings = sorted([
            name for name in self.manager._groupings
        ])

        for name in groupings:
            table.add_row(str(len(self.manager._groupings[name])), name)

        self.console.print(table)

    def _render_one_grouping(self, name: str) -> None:
        if self.manager._groupings is None:
            return
        if name not in self.manager._groupings:
            self.pwarning(f'warning: could not find grouping: {name}')
            return
        table = Table(title='GROUPING DATA')
        table.add_column(name)

        for entry in self.manager._groupings[name]:
            if entry != name:
                table.add_row(entry)

        self.console.print(table)

    def _clear_groupings(self) -> Optional[bool]:
        if self.confirm('CONFIRM: clear groupings data?'):
            self.manager._groupings = dict()
            return
        return False

    def _import_groupings(self, groupings_raw: str) -> None:
        return self.manager._import_groupings(groupings_raw)