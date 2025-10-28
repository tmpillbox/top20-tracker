from src.ResultGame import ResultGame


from typing import Dict, List, Optional


class ResultYear:

    def __init__(self, year: int) -> None:
        self._by_name = dict()
        self._by_gid = dict()
        self._by_rank = dict()

    @property
    def num_results(self) -> int:
        return len(self._by_rank)

    def register_game(self, rank: int, game: "ResultGame") -> None:
        self._by_name[game.name] = game
        self._by_rank[rank] = game

    def by_name(self, name: str) -> Optional["ResultGame"]:
        return self._by_name.get(name)

    def by_gid(self, gid: int) -> Optional["ResultGame"]:
        return self._by_gid.get(gid)

    def by_rank(self, rank: int) -> Optional["ResultGame"]:
        return self._by_rank.get(rank)

    def all_game_names(self) -> List[str]:
        return [ k for k in self._by_name ]

    @property
    def as_dict(self) -> Dict:
        obj = dict()
        for rank in sorted(self._by_rank, reverse=True):
            obj[str(rank)] = self.by_rank(rank).as_dict # type: ignore
        return obj

    @classmethod
    def from_dict(cls, year: int, year_data: Dict) -> "ResultYear":
        result_year = cls(year)
        for rank, rank_data in year_data.items():
            rank_int = int(rank)
            game = ResultGame.from_dict(rank_data)
            result_year.register_game(rank_int, game)
        return result_year