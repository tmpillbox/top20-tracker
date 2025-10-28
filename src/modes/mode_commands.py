import cmd2
import argparse

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from src.util.util import CALYEAR, Utility

if TYPE_CHECKING:
    from src.TrackerManager import TrackerManager
    from src.VoteGame import VoteGame
    from src.modes.modes import GamesMode, GroupingsMode, ManagerMode, ResultsMode, VotesMode

@cmd2.with_default_category('MODE')
class CmdModeControl(cmd2.CommandSet):
    def __init__(self, parent: "TrackerManager"):
        self.parent: "TrackerManager" = parent
        super().__init__()

    def _list_modes(self) -> List[str]:
        return self.parent._list_modes()

    end_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(end_parser)
    def do_end(self, ns: argparse.Namespace):
        self.parent._do_end()

    mode_parser = cmd2.Cmd2ArgumentParser()
    mode_parser.add_argument('mode', choices_provider=_list_modes)

    @cmd2.with_argparser(mode_parser)
    def do_mode(self, ns: argparse.Namespace) -> Optional[bool]:
        if ns.mode is None:
            self.parent.do_help('mode')
        elif ns.mode in self.parent._mode_maps:
            clazz: Type[ManagerMode] = self.parent._mode_maps[ns.mode]
            mode: ManagerMode = clazz(ns.mode, self.parent, list(), dict())
            self.parent._update_mode(mode)


@cmd2.with_default_category('GAMES')
class CmdGamesMode(cmd2.CommandSet):
    def __init__(self, parent: "GamesMode"):
        super().__init__()
        self.parent: "GamesMode" = parent

    def choices_game_name(self) -> List[str]:
        return self.parent.choices_game_name()

    list_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(list_parser)
    def do_list(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._render_games_table()

    show_parser = cmd2.Cmd2ArgumentParser()
    show_parser.add_argument(
        'game', type=str,
        choices_provider=choices_game_name
    )

    @cmd2.with_argparser(show_parser)
    def do_show(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._render_one_game(ns.game)

    add_parser = cmd2.Cmd2ArgumentParser()
    add_parser.add_argument('name', type=str, choices_provider=choices_game_name)

    @cmd2.with_argparser(add_parser)
    def do_add(self, ns: argparse.Namespace) -> Optional[bool]:
        self.parent.add_game(ns.name)
        import pdb; pdb.set_trace()
        return

    delete_parser = cmd2.Cmd2ArgumentParser()
    delete_parser.add_argument(
        '--force', action='store_true', default=False
    )
    delete_parser.add_argument(
        'game', type=str, choices_provider=choices_game_name
    )

    @cmd2.with_argparser(delete_parser)
    def do_delete(self, ns: argparse.Namespace) -> Optional[bool]:
        self.parent.delete_game(ns.game, ns.force)


# game_parser = cmd2.Cmd2ArgumentParser()
# game_parser.add_argument('--force', action='store_true', default=False) # type: ignore
# game_parser.add_argument( # type: ignore
#     'command', choices=[ 'list', 'show', 'add', 'delete' ] 
# )
# game_parser.add_argument(
#     'name', choices_provider=choices_game_name, default='', nargs='?' 
# )

# @cmd2.with_argparser(game_parser)
# def do_game(self, args: argparse.Namespace) -> None:
#     if not args.command or args.command not in [ 'list', 'show', 'add', 'delete' ]:
#         self.perror('Invalid command: must choose \'game show\', \'game add\', or \'game delete\'.')
#         return

#     match args.command: 
#         case 'list':
#             return self._render_games_table()
#         case 'show':
#                 if args.name is None or len(args.name) == 0:
#                     self.perror('game show: must provide game name(s)')
#                 match = self.partial_command(args.name, self._sorted_game_names())
#                 self._render_one_game(match)
#                 return
#         case 'add':
#             self.add_game(args.name)
#             return
#         case 'delete':
#             if args.name is None or len(args.name) == 0:
#                 self.perror('game delete: must specify game name(s)')
#                 return
#             self.delete_game(args.name, force=args.force)
#             return

#     self.perror('Invalid \'game\' command. You should not see this.')

@cmd2.with_default_category('VOTES')
class CmdVotesMode(cmd2.CommandSet):
    def __init__(self, parent: "VotesMode"):
        super().__init__()
        self.parent: "VotesMode" = parent

    @property
    def year(self) -> int:
        return self.parent.year

    def choices_game_name(self) -> List[str]:
        return self.parent.choices_game_name()

    vote_parser = cmd2.Cmd2ArgumentParser()
    vote_parser.add_argument( # type: ignore
        'vote', type=str
    )
    vote_parser.add_argument(
        'game', choices_provider=choices_game_name
    )

    @cmd2.with_argparser(vote_parser)
    def do_vote(self, args: argparse.Namespace) -> None:
        self.parent.set_vote(self.year, args.vote, args.game)

    delete_parser = cmd2.Cmd2ArgumentParser()
    delete_parser_cmd = delete_parser.add_subparsers()

    delete_vote_parser = cmd2.Cmd2ArgumentParser()
    delete_vote_parser.add_argument(
        '--force',
        default=False, action='store_true',
        help='force vote deletion without prompt'
    )
    delete_vote_parser.add_argument(
        'rank', type=str,
        help='rank of vote to delete'
    )

    @cmd2.as_subcommand_to('delete', 'vote', delete_vote_parser)
    def _delete_vote(self, ns: argparse.Namespace):
        if ns.rank is None:
            self.parent.do_help('delete')
            return
        game: Optional["VoteGame"] = self.parent._game_by_vote(ns.rank)
        if game is None:
            self.parent.perror(f'Vote not found: {ns.rank}')
            return
        self.parent.delete_vote(self.year, ns.rank, game.name, ns.force)

    delete_game_parser = cmd2.Cmd2ArgumentParser()
    delete_game_parser.add_argument(
        '--force',
        default=False, action='store_true',
        help='force vote deletion without prompt'
    )
    delete_game_parser.add_argument(
        'game', type=str,
        help='game name of vote to delete'
    )

    @cmd2.as_subcommand_to('delete', 'game', delete_game_parser)
    def _delete_game(self, ns: argparse.Namespace):
        if ns.game is None:
            self.parent.do_help('delete')
            return
        rank: Optional[str] = self.parent._vote_by_name(ns.game)
        if rank is None:
            self.parent.perror(f'Game not found: {ns.game}')
            return
        self.parent.delete_vote(self.year, rank, ns.game, ns.force)

    @cmd2.with_argparser(delete_parser)
    def do_delete(self, ns: argparse.Namespace) -> Optional[bool]:
        handler = ns.cmd2_handler.get()
        if handler is not None:
            handler(ns)
        else:
            self.parent.do_help('delete')

    list_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(list_parser)
    def do_list(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._render_votes_table()


@cmd2.with_default_category('GROUPINGS')
class CmdGroupingsMode(cmd2.CommandSet):
    def __init__(self, parent: "GroupingsMode"):
        super().__init__()
        self.parent: "GroupingsMode" = parent

    def perror(self, *args, **kwargs) -> Optional[bool]:
        return self.parent.perror(*args, **kwargs)

    def choices_groupings_name(self) -> List[str]:
        return self.parent.choices_groupings_name()

    groupings_parser = cmd2.Cmd2ArgumentParser()
    groupings_parser_cmd = groupings_parser.add_subparsers(dest='command', title='subcommands')

    groupings_parser_list: cmd2.Cmd2ArgumentParser = groupings_parser_cmd.add_parser('list')

    groupings_parser_show = groupings_parser_cmd.add_parser('show')
    groupings_parser_show.add_argument(
        'name', choices_provider=choices_groupings_name
    )

    groupings_parser_clear: cmd2.Cmd2ArgumentParser = groupings_parser_cmd.add_parser('clear')

    groupings_parser_import: cmd2.Cmd2ArgumentParser = groupings_parser_cmd.add_parser('import')
    groupings_parser_import.add_argument(
        'import_file', completer=cmd2.Cmd.path_complete,
        help='Path to raw groupings file'
    )

    list_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(list_parser)
    def do_list(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._render_groupings_table()

    show_parser = cmd2.Cmd2ArgumentParser()
    show_parser.add_argument(
        'name', choices_provider=choices_groupings_name
    )

    @cmd2.with_argparser(show_parser)
    def do_show(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._render_one_grouping(ns.name)

    import_parser = cmd2.Cmd2ArgumentParser()
    import_parser.add_argument(
        'import_file', completer=cmd2.Cmd.path_complete,
        help='Path to raw groupings file'
    )

    @cmd2.with_argparser(import_parser)
    def do_import(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._import_groupings(ns.import_file)

    clear_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._clear_groupings()


# @cmd2.with_argparser(groupings_parser)
# def do_groupings(self, args: argparse.Namespace) -> None:
#     if args.command is None:
#         self.perror('groupings: must choose subcommand: list, show, import, clear')
#         return
#     match args.command:
#         case 'list':
#             self.parent._render_groupings_table()
#         case 'show':
#             self.parent._render_one_grouping(args.name)
#         case 'import':
#             self.parent._import_groupings(args.import_file)
#         case 'clear':
#             self.parent._clear_groupings()
#         case _:
#             self.perror('groupings: must choose subcommand: list, show, import, clear')
#     return


@cmd2.with_default_category('RESULTS')
class CmdResultsMode(cmd2.CommandSet):
    def __init__(self, parent: "ResultsMode"):
        super().__init__()
        self.parent: "ResultsMode" = parent

    def choices_grouped_items(self) -> List[str]:
        return self.parent._choices_grouped_items()

    def choices_selected_grouped_items(self) -> List[str]:
        return self.parent._choices_selected_grouped_items()

    def choices_import_result_items(self, arg_tokens: Dict[str, Any]) -> List[str]:
        if 'year' in arg_tokens:
            return self.parent._choices_import_result_items(arg_tokens['year'])
        return self.parent._choices_import_result_items()

    def choices_result_years(self) -> List[int]:
        return self.parent._choices_result_years()

    select_parser = cmd2.Cmd2ArgumentParser()
    select_parser.add_argument('rank', type=int)

    @cmd2.with_argparser(select_parser)
    def do_select(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._results_select(ns.rank)

    clear_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(clear_parser)
    def do_clear(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._results_clear()

    next_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(next_parser)
    def do_next(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._results_next()

    show_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(show_parser)
    def do_show(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._results_show()

    # @cmd2.as_subcommand_to('results', 'show', show_parser)
    # def results_show(self, ns: argparse.Namespace):
    #     self.parent._results_show()

    list_parser = cmd2.Cmd2ArgumentParser()
    list_parser.add_argument(
        '--max-rank', type=int,
        help='Only show games ranked numerically equal to or lower than --max-rank'
    )
    list_parser.add_argument(
        '--min-rank', type=int,
        help='Only show games ranked numerically equal to or higher than --min-rank'
    )
    list_parser.add_argument(
        '--owned', type=Utility.str2bool,
        help='If specified, only show games either owned or not-owned'
    )
    list_parser.add_argument(
        '--prev-owned', type=Utility.str2bool,
        help='If specified, only show games either previously owned or not marked previously owned'
    )
    list_parser.add_argument(
        '--played', type=Utility.str2bool,
        help='If specified, only show games either played or unplayed'
    )
    list_parser.add_argument(
        '--wishlist', nargs='+',
        choices=[ 'no', 'Low', 'Medium', 'High' ],
        help='If specified, only show games matching one of the provided Wishlist priorities'
    )
    list_parser.add_argument(
        '--voted', type=Utility.str2bool,
        help='If specified, only show games either voted for or not voted for'
    )

    @cmd2.with_argparser(list_parser)
    def do_list(self, ns: argparse.Namespace) -> Optional[bool]:
        self.parent._render_results(ns)

    # @cmd2.as_subcommand_to('results', 'list', list_parser)
    # def results_list(self, ns: argparse.Namespace):
    #     self.parent._render_results(ns)

    mark_parser = cmd2.Cmd2ArgumentParser()
    mark_parser_cmd = mark_parser.add_subparsers(dest='command')

    mark_parser_own = mark_parser_cmd.add_parser('own')
    mark_parser_own.add_argument('val', type=Utility.str2bool)

    mark_parser_wishlist = mark_parser_cmd.add_parser('wishlist')
    mark_parser_wishlist.add_argument('val', choices=[ 'no', 'High', 'Medium', 'Low' ])

    mark_parser_played = mark_parser_cmd.add_parser('played')
    mark_parser_played.add_argument('val', type=Utility.str2bool)

    mark_parser_prev_owned = mark_parser_cmd.add_parser('prev_owned')
    mark_parser_prev_owned.add_argument('val', type=Utility.str2bool)

    mark_parser_items = mark_parser_cmd.add_parser('items')
    mark_parser_items_action = mark_parser_items.add_subparsers(dest='action')

    mark_parser_items_add = mark_parser_items_action.add_parser('add')
    mark_parser_items_add.add_argument('item', choices_provider=choices_grouped_items)

    mark_parser_items_del = mark_parser_items_action.add_parser('remove')
    mark_parser_items_del.add_argument('item', choices_provider=choices_selected_grouped_items)

    @cmd2.with_argparser(mark_parser)
    def do_mark(self, ns: argparse.Namespace) -> Optional[bool]:
        if ns.command is None:
            self.parent.do_help('mark')
            return
        match ns.command:
            case 'own':
                return self.parent._mark_own(ns.val)
            case 'prev_owned':
                return self.parent._mark_prev_owned(ns.val)
            case 'wishlist':
                return self.parent._mark_wishlist(ns.val)
            case 'played':
                return self.parent._mark_played(ns.val)
            case 'items':
                return self.parent._mark_owned_items(ns.action, ns.item)

    @cmd2.with_argparser(mark_parser_own)
    def do_own(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._mark_own(ns.val)

    @cmd2.with_argparser(mark_parser_prev_owned)
    def do_prev_owned(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._mark_prev_owned(ns.val)

    @cmd2.with_argparser(mark_parser_played)
    def do_played(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._mark_played(ns.val)

    @cmd2.with_argparser(mark_parser_wishlist)
    def do_wishlist(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._mark_wishlist(ns.val)

    @cmd2.with_argparser(mark_parser_items)
    def do_items(self, ns: argparse.Namespace) -> Optional[bool]:
        return self.parent._mark_owned_items(ns.action, ns.item)

    add_parser = cmd2.Cmd2ArgumentParser()
    add_parser.add_argument(
        'game', type=str,
        help='Name of the game'
    )

    @cmd2.with_argparser(add_parser)
    def do_add(self, ns: argparse.Namespace) -> Optional[bool]:
        self.parent.set_add(ns.game)

    import_parser = cmd2.Cmd2ArgumentParser()
    import_parser.add_argument(
        '--year', '-Y',
        choices_provider=choices_result_years,
        help='specify a year to import from. default is previous year'
    )
    import_parser.add_argument(
        'game', type=str,
        choices_provider=choices_import_result_items
    )

    @cmd2.with_argparser(import_parser)
    def do_import(self, ns: argparse.Namespace) -> Optional[bool]:
        if ns.year is None:
            year = CALYEAR - 1
        else:
            year = ns.year
        self.parent.set_import(ns.game)