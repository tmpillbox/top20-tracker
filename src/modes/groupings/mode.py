from src.modes.mode import ManagerMode
from src.modes.groupings.cmd_set import CmdGroupingsMode


from rich.table import Table


from typing import List, Optional


class GroupingsMode(ManagerMode):
    _cmd_sets = [ CmdGroupingsMode ]

    def choices_groupings_name(self) -> List[str]:
        return self.manager.choices_groupings_name()

    def _render_groupings_table(self) -> None:
        if self.manager._groupings is None:
            return
        table = Table(title='Groupings')
        table.add_column('# Entries')
        table.add_column('Grouping')
        groupings = sorted([
            name for name in self.manager._groupings
        ])

        for name in groupings:
            table.add_row(str(len(self.manager._groupings[name])), name)

        self.console.print(table)

    def _render_one_grouping(self, name: str) -> None:
        if self.manager._groupings is None:
            return
        if name not in self.manager._groupings:
            self.pwarning(f'warning: could not find grouping: {name}')
            return
        table = Table(title='GROUPING DATA')
        table.add_column(name)

        for entry in self.manager._groupings[name]:
            if entry != name:
                table.add_row(entry)

        self.console.print(table)

    def _clear_groupings(self) -> Optional[bool]:
        if self.confirm('CONFIRM: clear groupings data?'):
            self.manager._groupings = dict()
            return
        return False

    def _import_groupings(self, groupings_raw: str) -> None:
        return self.manager._import_groupings(groupings_raw)