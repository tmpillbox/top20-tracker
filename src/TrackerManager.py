from src.modes.groupings.mode import GroupingsMode
from src.modes.results.mode import ResultsMode
from src.modes.votes.mode import VotesMode
from src.modes.games.mode import GamesMode
from src.core.cmd_set_mode_control import CmdModeControl
from src.models.results import Results, ResultGame
from src.models.votes import VoteGame


import cmd2
from rich.console import Console
from rich.table import Table


import argparse
import json
import pdb
import shlex
from typing import Dict, Iterator, List, Optional, Set, Tuple, Type, Union

from src.modes.mode import ManagerMode


class TrackerManager(cmd2.Cmd):
    _static_cmds = [
        CmdModeControl
    ]
    _mode_maps: Dict[str, Type[ManagerMode]] = {
        'votes': VotesMode,
        'results': ResultsMode,
        'groupings': GroupingsMode,
        'games': GamesMode
    }

    @staticmethod
    def partial_command(arg_string: str, choices: List[str]) -> str:
        """Returns a full match from a partial string, or raises an error."""
        matches = [ c for c in choices if c.startswith(arg_string) ]

        if not matches:
            raise argparse.ArgumentTypeError(f"Invalid choice: '{arg_string}' (choose from {choices})")
        elif len(matches) > 1:
            raise argparse.ArgumentTypeError(f"Ambiguous choice: '{arg_string}' (matches {matches})")
        else:
            return matches[0]

    @staticmethod
    def positive_integer(int_val: str):
        """Returns a valid positive integer or raises an error"""

        if not int_val.isdigit():
            raise argparse.ArgumentTypeError(f"Not an integer: {int_val}")
        elif int(int_val) <= 0:
            raise argparse.ArgumentTypeError(f"Not a positive integer: {int_val}")
        else:
            return int(int_val)

    @staticmethod
    def combobulate_line(args: List[str]):
        return ' '.join([ shlex.quote(arg) for arg in args ])

    def __init__(self, votes_file: str, groupings_file: str, results_file: str, year: int, interactive: bool = False):
        super(TrackerManager, self).__init__(allow_cli_args=False, include_ipy=True, include_py=True)

        # self.register_command_set(CmdResults(self))
        for cmd_set in self._static_cmds:
            self.register_command_set(cmd_set(self))

        self.console = Console()
        self._votes_file = votes_file
        self._groupings_file = groupings_file
        self._results_file = results_file
        self._votes = None
        self._groupings = None
        self._results = Results()
        self.year = year
        self.interactive = interactive
        self.mode = None
        self.selected_result = None
        self._update_prompt()
        self._load_vote_data()
        self._load_groupings_data()
        self._load_results_data()

    def _update_mode(self, mode: Optional[ManagerMode]) -> None:
        """Do mode update de-init and init"""
        if self.mode is not None:
            self.mode.teardown(self)
        self.mode = mode
        if self.mode is not None:
            self.mode.setup(self)
        self._update_prompt()

    def _do_end(self) -> None:
        """Clear mode selection"""
        self._update_mode(None)

    def do_config(self, statement: Union[cmd2.Statement, str]) -> Optional[bool]:
        return super().do_set(statement)

    debug_parser = cmd2.Cmd2ArgumentParser()
    debug_parser.add_argument(
        'status', choices = [ 'true', 'false' ]
    )

    @cmd2.with_argparser(debug_parser)
    def do_debug(self, ns: argparse.Namespace) -> Optional[bool]:
        self.onecmd(f'config debug {ns.status}')

    # results_parser: cmd2.Cmd2ArgumentParser = cmd2.Cmd2ArgumentParser()
    # results_parser_cmd = results_parser.add_subparsers()

    # @cmd2.with_argparser(results_parser)
    # def do_results(self, ns: argparse.Namespace):
    #     handler = ns.cmd2_handler.get()
    #     if handler is not None:
    #         handler(ns)
    #     else:
    #         self.do_help('results')

    # def _results_select(self, rank: int) -> None:
    #     self.hier = f'results {rank}'
    #     self._update_prompt()

    # def _results_clear(self) -> None:
    #     self.hier = ''
    #     self._update_prompt()

    # def _results_next(self) -> None:
    #     if self.hier.startswith('results '):
    #         curr_rank = shlex.split(self.hier)[-1]
    #         next_rank = int(curr_rank) - 1
    #         self._results_select(next_rank)

    def _list_modes(self) -> List[str]:
        return list(self._mode_maps.keys())

    def _update_year(self, _param_name, _old, new) -> None:
        self._update_prompt()

    def _load_vote_data(self) -> None:
        try:
            with open(self._votes_file, 'r') as f:
                self._votes = json.load(f)
        except FileNotFoundError:
            self._votes = dict()
            self._save_votes_data()

    def _save_votes_data(self) -> None:
        with open(self._votes_file, 'w') as f:
            json.dump(self._votes, f, indent=4)

    def _load_groupings_data(self) -> None:
        try:
            with open(self._groupings_file, 'r') as f:
                self._groupings = json.load(f)
        except FileNotFoundError:
            self._groupings = dict()
            self._save_groupings_data()

    def _save_groupings_data(self) -> None:
        with open(self._groupings_file, 'w') as f:
            json.dump(self._groupings, f, indent=4)

    def _import_groupings(self, groupings_raw: str) -> None:
        try:
            with open(groupings_raw, 'r') as f:
                raw_groupings = json.load(f)
        except:
            import pdb; pdb.set_trace()
            return
        if not isinstance(raw_groupings, list):
            self.perror('error: groupings import: invalid data')
            return
        for group in raw_groupings:
            lead_game = group['leadGame']['name']
            if lead_game in self._groupings:
                self.pwarning(f'EXISTING GROUP: replacing {lead_game}')
                del self._groupings[lead_game] # type: ignore
            names = [ game['name'] for game in group['games'] ]
            for name in names:
                existing = self._game_in_grouping(name)
                if existing is not None:
                    self.pwarning(f'warning: game {name} found in existing grouping: {existing}')
            self._groupings[lead_game] = list(set(names)) # type: ignore

    def _load_results_data(self) -> None:
        try:
            with open(self._results_file, 'r') as f:
                results = json.load(f)
                self._results = Results.from_dict(results)
        except FileNotFoundError:
            self._results = Results()
            self._save_results_data()

    def _save_results_data(self) -> None:
        with open(self._results_file, 'w') as f:
            json.dump(self._results.as_dict, f, indent=4)

    def _update_prompt(self) -> None:
        if self.mode is not None:
            mode = str(self.mode)
        else:
            mode = ''
        self.prompt = f'{self.year}{mode}> '

    def get_year_data(self, year: Union[str, int]) -> dict:
        year = str(year)
        year_data = dict()
        if self._votes is None:
            return year_data
        for name, data in self._votes.items():
            game = VoteGame(name, data)
            vote = game.year_rank(year)
            if vote:
                year_data[vote] = game
        return year_data

    def set_vote(self, year: int, vote: str, game: str) -> Optional[bool]:
        if self._votes is None:
            self._votes = dict()
        if game not in self._votes:
            self.perror(f'"{game}" not found. Please add it first using the "game" command')
            return False
        # Check if there's already a game with the current year and current vote
        year_data = self.get_year_data(year)
        if vote in year_data:
            # Remove vote
            try_del = self.delete_vote(year, vote, game)
            if try_del is False:
                # Delete failed, bail
                return False
        if 'vote_ranks' not in self._votes[game]:
            self._votes[game]["vote_ranks"] = dict()
        self._votes[game]["vote_ranks"][str(year)] = str(vote)
        return

    def confirm(self, message: str, default=False) -> Optional[bool]:
        while True:
            response = input(f'{message} (y/n): ').lower()

            if response in ['y', 'yes']:
                return
            elif response in ['n', 'no']:
                return False
            elif response == '':
                # Cancel
                self.perror('Cancelled')
                return default
            else:
                self.perror('Invalid response. Please answer \'y\' or \'n\'.')

    def delete_vote(self, year: int, vote: str, game: str, force: bool = False) -> Optional[bool]:
        year_data = self.get_year_data(year)
        if vote in year_data:
            if year_data[vote].name != game:
                self.perror(f'Mismatch! This shouldn\'t happen. Please consult your nearest Tyler McGeorge')
                return False
            if force or self.confirm('CONFIRM: delete vote {vote} for game {game}?'):
                if self._votes is not None:
                    del self._votes[game]["vote_ranks"][str(year)]

    def add_game(self, name: str) -> Optional[bool]:
        if self._votes is None:
            self._votes = dict()
        if name in self._votes:
            # Game exists
            self.pwarning(f'Game "{name}" already exists')
            return False
        self._votes[name] = dict()
        self._votes[name]['vote_ranks'] = dict()

    def delete_game(self, name: str, force: bool = False) -> Optional[bool]:
        if self._votes is None:
            self._votes = dict()
        if name in self._votes:
            if self._votes[name]["vote_ranks"]:
                # Game has votes registered
                self.perror(f'Cannot delete game "{name}". {len(self._votes[name]["vote_ranks"])} votes recorded for game.')
                return False
            if force or self.confirm('CONFIRM: delete game "{name}"?'):
                del self._votes[name]
                return
        elif not force:
            self.perror(f'Unable to delete game: does not exist: {name}')
            return False
        return False

    @property
    def max_vote(self) -> int:
        year = self.get_year_data(self.year)
        if not year:
            return 0
        return max( year.keys() )

    def choices_game_name(self) -> List[str]:
        return self._sorted_game_names()

    def choices_all_grouped_games(self) -> List[str]:
        names = list()
        if self._groupings is None:
            return names
        for group, games in self._groupings.items():
            if group not in games:
                names.append(group)
            for game in games:
                names.append(game)
        return names

    def choices_groupings_name(self) -> List[str]:
        return self._sorted_groupings_names()

    def _sorted_game_names(self) -> List[str]:
        if self._votes is None:
            return list()
        return sorted([ k for k in self._votes.keys() ])

    def _choices_grouped_items(self, target: str) -> List[str]:
        if target:
            # target could be rank or game name
            if target.isdigit():
                year_data = self._results.year(self.year)
                if year_data is not None:
                    game_name = year_data.by_rank(int(target))
                    if game_name is not None:
                        game_name = game_name.name
                    if game_name is None:
                        group = self._game_in_grouping(target)
                        if self._groupings and group:
                            return self._groupings[group]
                    if game_name is None:
                        return list()
                    group = self._game_in_grouping(game_name)
                    if self._groupings and group:
                        return self._groupings[group]
            else:
                group = self._game_in_grouping(target)
                if self._groupings and group:
                    return self._groupings[group]
        return list()

    def _choices_selected_grouped_items(self, target: str) -> List[str]:
        if target:
            # target could be rank or game
            if target.isdigit():
                year_data = self._results.year(self.year)
                if year_data is not None:
                    game_name = year_data.by_rank(int(target))
                    if game_name is not None:
                        game_name = game_name.name
                    if game_name is not None:
                        group = self._game_in_grouping(game_name)
                        if self._groupings and group:
                            return self._groupings[group]
                    return list()
            else:
                group = self._game_in_grouping(target)
                if self._groupings and group:
                    return self._groupings[group]
        return list()

    def _sorted_groupings_names(self) -> List[str]:
        if self._groupings is not None:
            return sorted([ k for k in self._groupings.keys() ])
        return list()

    check_game_grouping_parser = cmd2.Cmd2ArgumentParser()
    check_game_grouping_parser.add_argument('game', type=str, choices_provider=choices_all_grouped_games)

    @cmd2.with_argparser(check_game_grouping_parser)
    def do_check_game_grouping(self, ns: argparse.Namespace) -> Optional[bool]:
        self.poutput(str(self._game_in_grouping(ns.game)))
        return

    def _game_in_grouping(self, name: str) -> Union[None, str]:
        if self._groupings is None:
            return None
        if name in self._groupings: # type: ignore
            return name
        for group, entries in self._groupings.items():
            if name in entries:
                return group
        return None

    def _game_by_vote(self, rank: Union[int, str]) -> Optional[VoteGame]:
        year = self.get_year_data(self.year)
        rank = str(rank)
        if rank in year:
            return year[rank]
        return None

    def _vote_by_game(self, game: str) -> Optional[str]:
        year = self.get_year_data(self.year)
        for rank in year:
            if game == year[rank]:
                return rank
        return None

    def _render_votes_table(self) -> None:
        table = Table(title='Votes')

        table.add_column('VOTE')
        table.add_column('GAME')

        year_data = self.get_year_data(self.year)
        max_vote = 0
        for vote_rank in year_data:
            if vote_rank.isdigit():
                max_vote = max(max_vote, int(vote_rank))

        votes_seen = set()

        for vote_rank in range(max_vote):
            votes_seen.add(str(vote_rank + 1))
            game = self._game_by_vote(vote_rank + 1)
            if game is None:
                name = ''
            else:
                name = game.name
            table.add_row(str(vote_rank + 1), name)

        for vote_rank, game in year_data.items():
            if vote_rank in votes_seen:
                continue
            table.add_row(vote_rank, game.name)
        self.console.print(table)

    def _render_games_table(self) -> None:
        if self._votes is None:
            return
        table = Table(title='Games')
        table.add_column('Game')
        game_names = sorted([
            name for name in self._votes
        ])

        for name in game_names:
            table.add_row(name)

        self.console.print(table)

    def _render_one_game(self, game_name: str) -> None:
        table = Table(title=game_name)
        grouping = self._game_in_grouping(game_name)
        if grouping is not None:
            table.caption = f'In Grouping: {grouping}'
        table.add_column('YEAR')
        table.add_column('VOTE')
        if self._votes:
            for year, vote in self._votes[game_name]["vote_ranks"].items():
                table.add_row(year, vote)

        self.console.print(table)

    def vote_by_name(self, name: str) -> str:
        if self._votes is None:
            return "N/A"
        if name in self._votes and str(self.year) in self._votes[name]['vote_ranks']:
            return self._votes[name]['vote_ranks'][str(self.year)]
        return "N/A"

    def _all_result_games(self, src_year: Optional[Union[str, int]]) -> List[str]:
        all_games: Set[str] = set()
        if src_year is None:
            for year in self._results.years.values():
                for game in year.all_game_names():
                    all_games.add(game)
        elif not str(src_year).isdigit():
            return list(all_games)
        else:
            year = self._results.year(int(src_year))
            if year is None:
                return list(all_games)
            for game in year.all_game_names():
                all_games.add(game)
        return list(all_games)

    def get_result_year_items(self, year: int) -> Iterator[Tuple[int, ResultGame]]:
        result_year = self._results.year(year)
        if result_year is None or not result_year._by_rank:
            return
        ranks = sorted(result_year._by_rank, reverse=True)
        for rank in ranks:
            item = result_year.by_rank(rank)
            if item is not None:
                yield (rank, item)

    def _render_results(self, ns: argparse.Namespace) -> None:
        table = Table(title="Results")

        table.add_column('RANK')
        table.add_column('GAME')
        table.add_column('OWN')
        table.add_column('SOLD')
        table.add_column('WANT')
        table.add_column('PLAYED')
        table.add_column('VOTED')

        result_rows: int = 0

        rank: int
        result: ResultGame
        for rank, result  in self.get_result_year_items(self.year):
            match result.wishlist:
                case 'no':
                    wish = '×'
                case 'High':
                    wish = '▀'
                case 'Medium':
                    wish = '•'
                case 'Low':
                    wish = '▄'
                case _:
                    wish = '?'

            vote = self.vote_by_name(result.name)

            if ns.max_rank is not None:
                if ns.max_rank < rank:
                    continue
            if ns.min_rank is not None:
                if ns.min_rank > rank:
                    continue
            if ns.owned is not None:
                if ns.owned != result.own:
                    continue
            if ns.prev_owned is not None:
                if ns.prev_owned != result.prev_owned:
                    continue
            if ns.played is not None:
                if ns.played != result.played:
                    continue
            if ns.wishlist is not None:
                if result.wishlist not in ns.wishlist:
                    continue
            if ns.voted is not None:
                if ns.voted and vote == 'N/A':
                    continue
                if not ns.voted and vote != 'N/A':
                    continue

            table.add_row(
                str(rank),
                result.name,
                'Y' if result.own else 'N',
                'Y' if result.prev_owned else 'N',
                wish,
                'Y' if result.played else 'N',
                vote
            )
            result_rows += 1

        self.console.print(table)
        self.poutput(f'{result_rows} results')

    # delete_parser: cmd2.Cmd2ArgumentParser = cmd2.Cmd2ArgumentParser()
    # delete_parser.add_argument(
    #     '--force', action='store_true', default=False
    # )
    # delete_parser_typ = delete_parser.add_subparsers(dest='command', title='commands')
    # delete_typ_vote: cmd2.Cmd2ArgumentParser = delete_parser_typ.add_parser('vote')
    # delete_typ_vote.add_argument(
    #     'vote', type=str
    # )

    # delete_typ_game: cmd2.Cmd2ArgumentParser = delete_parser_typ.add_parser('game')
    # delete_typ_game.add_argument(
    #     'game', type=str,
    #     choices_provider=choices_game_name
    # )

    # @cmd2.with_argparser(delete_parser)
    # def do_delete(self, args: argparse.Namespace) -> None:
    #     if not args.command or args.command not in [ 'vote', 'game' ]:
    #         self.perror('invalid delete command: "delete vote" or "delete game" is required')
    #         return
    #     match args.command:
    #         case 'vote':
    #             year = int(self.year)
    #             vote = str(args.vote)
    #             year_data = self.get_year_data(year)
    #             if vote in year_data:
    #                 self.delete_vote(year, vote, year_data[vote].name, force=args.force)
    #         case 'game':
    #             if args.game in self._votes:
    #                 self.delete_game(args.game, force=args.force)

    # show_parser = cmd2.Cmd2ArgumentParser()
    # show_parser_typ = show_parser.add_subparsers(dest='command', title='commands')
    # show_typ_votes = show_parser_typ.add_parser('votes')

    # show_typ_games: cmd2.Cmd2ArgumentParser = show_parser_typ.add_parser('games')
    # show_typ_games.add_argument(
    #     'name', nargs='*', type=str,
    #     choices_provider=choices_game_name
    # )

    # @cmd2.with_argparser(show_parser)
    # def do_show(self, args: argparse.Namespace) -> None:
    #     command = args.command
    #     if command is None:
    #         # Default to show votes
    #         self._render_votes_table()
    #         return
    #     match command:
    #         case 'games':
    #             game_names = self._sorted_game_names()
    #             if args.name:
    #                 for name in args.name:
    #                     if name in game_names:
    #                         self._render_one_game(name)
    #                     else:
    #                         self.perror(f'No data found: {name}')
    #                 return
    #             self._render_games_table()
    #         case 'votes':
    #             self._render_votes_table()
    #         case _:
    #             print (f"not found: {command}")


    results_parser: cmd2.Cmd2ArgumentParser = cmd2.Cmd2ArgumentParser()
    results_parser_cmd = results_parser.add_subparsers(dest='command', title='subcommands')

    #results_parser_show = 

    rollback_parser: cmd2.Cmd2ArgumentParser = cmd2.Cmd2ArgumentParser()
    rollback_parser.add_argument('data', choices=[ 'all', 'votes', 'results', 'groupings' ])

    save_parser: cmd2.Cmd2ArgumentParser = cmd2.Cmd2ArgumentParser()
    save_parser.add_argument('data', choices=[ 'all', 'votes', 'results', 'groupings'] )

    @cmd2.with_argparser(rollback_parser)
    def do_rollback(self, args) -> None:
        if args.data in [ 'all', 'votes' ]:
            self._load_vote_data()
            self.pfeedback(f'LOADED {len(self._votes)} voting record games') # type: ignore
        if args.data in [ 'all', 'results' ]:
            self._load_results_data()
            self.pfeedback(f'LOADED {sum([ len(v) for v in self._results.values() ])} results from {len(self._results)} years') # type: ignore
        if args.data in [ 'all', 'groupings' ]:
            self._load_groupings_data()
            self.pfeedback(f'LOADED {sum([ len(v) for v in self._groupings.values() ])} entries in {len(self._groupings)} groups') # type: ignore

    @cmd2.with_argparser(save_parser)
    def do_save(self, args) -> None:
        if args.data in [ 'all', 'votes' ]:
            self._save_votes_data()
            self.pfeedback(f'SAVED {len(self._votes)} games') # type: ignore
        if args.data in [ 'all', 'results' ]:
            self._save_results_data()
            self.pfeedback(f'SAVED {self._results.num_results} results from {self._results.num_years} years')
        if args.data in [ 'all', 'groupings' ]:
            self._save_groupings_data()
            self.pfeedback(f'SAVED {sum([ len(v) for v in self._groupings.values() ])} entries in {len(self._groupings)} groups') # type: ignore

    year_parser = cmd2.Cmd2ArgumentParser()
    year_parser.add_argument('year', type=int)

    @cmd2.with_argparser(year_parser)
    def do_year(self, args: argparse.Namespace) -> None:
        if args.year is not None:
            self.year = args.year
            self.poutput(f'Changed year to {self.year}')
            self._update_prompt()
        else:
            self.perror(f'Invalid year: {args.year}')