import cmd2
import argparse

from src.models.votes.vote_game import VoteGame

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.modes.votes.mode import VotesMode

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