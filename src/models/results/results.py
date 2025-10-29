from .result_game import ResultGame
from .result_year import ResultYear

from typing import Dict, Optional


class Results:
    def __init__(self) -> None:
        self.years: Dict[int, ResultYear] = dict()

    @property
    def num_years(self) -> int:
        return len(self.years)

    @property
    def num_results(self) -> int:
        return sum([ y.num_results for y in self.years.values() ])

    def add_year(self, year: int) -> None:
        if year not in self.years:
            self.years[year]  = ResultYear(year)

    def add_result(self, year: int, rank: int, result: ResultGame) -> None:
        if year not in self.years:
            self.add_year(year)
        self.years[year].register_game(rank, result)

    def year(self, year: int) -> Optional[ResultYear]:
        return self.years.get(year)

    @property
    def as_dict(self) -> Dict:
        obj = dict()
        for year in sorted(self.years.keys()):
            year_data = self.years[year]
            obj[str(year)] = year_data.as_dict
        return obj

    @classmethod
    def from_dict(cls, data: Dict) -> "Results":
        results: "Results" = cls()
        for year, year_data in data.items():
            int_year = int(year)
            results_year: "ResultYear" = ResultYear.from_dict(int_year, year_data)
            results.years[int_year] = results_year
        return results