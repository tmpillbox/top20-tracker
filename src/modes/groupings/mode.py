from src.modes.mode import ManagerMode
from src.modes.groupings.cmd_set import CmdGroupingsMode


from rich.table import Table


from typing import List, Optional


class GroupingsMode(ManagerMode):
    _cmd_sets = [ CmdGroupingsMode ]

    def choices_groupings_name(self) -> List[str]:
        return self.manager.choices_groupings_name()
    
    def _choices_selected_grouped_items(self, group: str) -> List[str]:
        items = self.manager.get_group(group)
        if items is None:
            return list()
        return items

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

    def promote_group_item(self, group: str, root_item: str) -> None:
        if self.manager._groupings is None:
            return
        if group == root_item:
            return
        new_items = [ root_item ]
        old_items = self.manager._groupings[group]
        for item in old_items:
            if item in new_items:
                continue
            new_items.append(item)
        del self.manager._groupings[group]
        self.manager._groupings[root_item] = new_items
