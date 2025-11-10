import argparse

from rich.table import Table
from rich.text import Text

from src.modes.mode import ManagerMode
from src.modes.results.cmd_set import CmdResultsMode
from src.models.results import ResultYear, ResultGame

from typing import TYPE_CHECKING, List, Optional, Union

from src.util.markup import Markup

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
            curr_rank = self._get_lowest_rank()
        if curr_rank == 1:
            self.pwarning('results: cannot advance beyond #1')
            return
        self.context = [ str(curr_rank - 1) ]
        self.manager._update_prompt()

    def _results_prev(self) -> None:
        curr_rank = self._get_context_rank()
        if curr_rank is None:
            curr_rank = self._get_highest_rank()
        self.context = [ str(curr_rank + 1) ]
        self.manager._update_prompt()

    def _get_context_rank(self) -> Optional[int]:
        if not self.context:
            return None
        try:
            return int(self.context[0])
        except:
            return None
        return None
    
    def _get_highest_rank(self) -> int:
        year = self.manager.get_result_year(self.year)
        if year is None:
            return 200
        return year.highest_rank()
    
    def _get_lowest_rank(self) -> int:
        year = self.manager.get_result_year(self.year)
        if year is None:
            return 200
        return year.lowest_rank()


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
    
    @staticmethod
    def vote_position(position, rank, game_name):
        row_markup = Markup.markup_row(rank)
        if rank is not None and rank != "N/A":
            result = f'{rank:>4}'
        else:
            result = '   ?'
            game_name = ''.join([ '?' ] * len(game_name))
        rank_result = (
            f'#{position:>2} ({result})',
            f'bold {row_markup}'
        )
        return Text.assemble(
            rank_result,
            ('  '),
            (game_name.ljust(65 - len(rank_result[0])), row_markup)
        )
    
    @staticmethod
    def _coerce_wishlist_priority(wishlist_priority: str) -> str:
        coercion_map = {
            'H': 'H',
            'HIGH': 'H',
            'HI': 'H',
            'M': 'M',
            'MED': 'M',
            'MEDIUM': 'M',
            'L': 'L',
            'LO': 'L',
            'LOW': 'L'
        }
        if wishlist_priority.upper() in coercion_map:
            return coercion_map[wishlist_priority.upper()]
        return 'no'
    
    @staticmethod
    def _output_summary_game_item(rank, game_name, wishlist_priority='no'):
        row_markup = Markup.markup_row(rank)
        wishlist_priority = ResultsMode._coerce_wishlist_priority(wishlist_priority)
        if wishlist_priority not in ('H', 'M', 'L'):
            name_format = game_name.ljust(61)
            if len(name_format) > 61:
                name_format = name_format[:58] + '...'
        else:
            name_format = game_name.ljust(58)
            if len(name_format) > 58:
                name_format = name_format[:55] + '...'
            name_format = f'{name_format}({wishlist_priority})'
        return Text.assemble(
            ('#', row_markup),
            (f'{rank:>4}', f'{row_markup} bold'),
            (f' {name_format}', row_markup)
        )


    def show_summary(self, short=False) -> None:

        revealed_count = self.manager.num_revealed_results()
        total_owned = 0
        total_wishlist = 0

        output: List[Union[str, Text]] = [
            "╔═════════════════════════════════════════════════════════════════════╗",
            "║                       PILLBOX'S GAME STATISTICS                     ║",
            "╠═════════╤═══════════╤═══════════╤═══════════╤═══════════╤═══════════╣",
        ]

        for n in range(200, 1, -10):
            hi, low = n, n - 9
            range_label = f'{hi:>3}-{low:>3}'
            results_found = 0
            own_count = 0
            sold_count = 0
            want_count = 0
            played_count = 0
            voted_count = 0

            for n in range(low, hi + 1):
                result = self.get_result(n)
                if result is None:
                    continue
                results_found += 1
                own_count += 1 if result.own else 0
                sold_count += 1 if result.prev_owned else 0
                want_count += 1 if result.wishlist != 'no' else 0
                played_count += 1 if result.played else 0
                voted_count += 1 if self.manager.vote_by_name(result.name) != "N/A" else 0
            
            total_owned += own_count
            total_wishlist += want_count
            
            if results_found == 0:
                continue

            row_markup_style = Markup.markup_row(hi)
            range_markup = (range_label, f'{row_markup_style} bold')

            own_markup = (f'OWN{own_count:>6}', row_markup_style)
            sold_markup = (f'SOLD{sold_count:>5}', row_markup_style)
            want_markup = (f'WANT{want_count:>5}', row_markup_style)
            played_markup = (f'PLAYED{played_count:>3}', row_markup_style)
            voted_markup = (f'VOTED{voted_count:>4}', row_markup_style)

            if n < 200 and n % 50 == 0:
                output.append('╠═════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╣')

            line = Text.assemble(
                ('║ '),
                range_markup,
                (' │ '),
                own_markup,
                (' ┊ '),
                sold_markup,
                (' ┊ '),
                want_markup,
                (' ┊ '),
                played_markup,
                (' ┊ '),
                voted_markup,
                (' ║')
            )
            output.append(line)
        
        if short:
            output.append('╚═════════════════════════════════════════════════════════════════════╝')
            for line in output:
                self.manager.console.print(line)
            return

        output.append('╠═════════╧═══════════╧═══════════╧═══════════╧═══════════╧═══════════╣')

        for v in range(1, 21):
            vote = self._game_by_vote(str(v))
            if vote is None:
                continue

            result = self.result_by_name(vote.name)
            if result is None:
                rank = None
            else:
                rank = self.rank_by_result(result)

            output.append(
                Text.assemble(
                   '║ ',
                   self.vote_position(v, rank, vote.name),
                   ' ║'
                )
            )

        output.append('╠═════════════════════════════════════════════════════════════════════╣')

        # Owned games
        year = self.manager.get_result_year(self.year)
        if year is not None:
            output.append(
                Text.assemble(
                    f'║                                                  OWN ',
                    Text(f'{total_owned:>3} / {revealed_count:>3}', style="bold"),
                    '      ║'
                )
            )
            for rank in range(self._get_highest_rank(), self._get_lowest_rank() - 1, -1):
                result = year.by_rank(rank)
                if result is None:
                    continue
                if result.own:
                    if result.owned_items:
                        for item in result.owned_items:
                            output.append(Text.assemble(
                                '║ ',
                                self._output_summary_game_item(rank, item),
                                ' ║'
                            ))
                    else:
                        output.append(Text.assemble(
                            f'║ ',
                            self._output_summary_game_item(rank, result.name),
                            ' ║'
                        ))
        else:
            output.append('║                      ERROR: RESULTS NOT FOUND                       ║')

        output.append('╠═════════════════════════════════════════════════════════════════════╣')

        # Wishlist games
        if year is not None:
            output.append(
                Text.assemble(
                    f'║                                             WISHLIST ',
                    Text(f'{total_wishlist:>3} / {revealed_count:>3}', style="bold"),
                    '      ║'
                )
            )
            for rank in range(self._get_highest_rank(), self._get_lowest_rank() - 1, -1):
                result = year.by_rank(rank)
                if result is None:
                    continue
                if result.wishlist != 'no': 
                    output.append(Text.assemble(
                        f'║ ',
                        self._output_summary_game_item(rank, result.name, wishlist_priority=result.wishlist),
                        ' ║'
                    ))
        else:
            output.append('║                      ERROR: RESULTS NOT FOUND                       ║')
        
        output.append('╚═════════════════════════════════════════════════════════════════════╝')

        for line in output:
            self.console.print(line)
