import cmd2
import argparse

from src.util.util import CALYEAR, Utility


from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.modes.results.mode import ResultsMode

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