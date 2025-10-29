import argparse

from rich.table import Table

from src.modes.mode import ManagerMode
from src.modes.results.cmd_set import CmdResultsMode
from src.models.results import ResultYear, ResultGame

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from src.modes.results.mode import ResultsMode
    from src.models.results import Results

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
        curr_rank = self._get_context_rank()
        if curr_rank is None:
            self.perror('results: must select rank before next')
            return
        if curr_rank == 1:
            self.warning('results: cannot advance beyond #1')
            return
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

    def _results_show(self, show_unowned=False) -> None:
        rank = self._get_context_rank()

        if rank is None:
            self.perror('results: no rank to show. select rank first')
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

        if show_unowned:
            unowned_items = list()
            items = self._choices_grouped_items()
            for item in items:
                if item not in result.owned_items:
                    unowned_items.append(item)
            table.add_row('UNOWNED ITEMS', '\n'.join(unowned_items))


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