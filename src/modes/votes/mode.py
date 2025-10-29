from src.modes.mode import ManagerMode
from src.modes.votes.cmd_set import CmdVotesMode


class VotesMode(ManagerMode):
    _cmd_sets = [ CmdVotesMode ]