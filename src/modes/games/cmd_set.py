import cmd2
import argparse

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.modes.games.mode import GamesMode

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

