# @cmd2.with_argparser(mode_parser)
# def do_mode(self, ns: argparse.Namespace) -> Optional[bool]:
#     handler = ns.cmd2_handler.get()
#     if handler is not None:
#         handler(ns)
#     else:
#         self.parent.do_help('mode')


from typing import Optional, Union


class VoteGame:
    def __init__(self, name: str, data: dict) -> None:
        self.name = name
        self.data = data

    def has_year(self, year: Union[str, int]) -> bool:
        year = str(year)
        if "vote_ranks" in self.data:
            return year in self.data["vote_ranks"]
        return False

    def year_rank(self, year: Union[str, int]) -> Optional[str]:
        year = str(year)
        if self.has_year(year):
            return self.data["vote_ranks"][year]
        return None