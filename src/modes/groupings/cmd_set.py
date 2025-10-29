import cmd2
import argparse

from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .mode import GroupingsMode

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

