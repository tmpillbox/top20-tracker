import cmd2
import argparse

from typing import TYPE_CHECKING, List, Optional, Type

if TYPE_CHECKING:
    from src.tracker_manager import TrackerManager
    from src.modes.mode import ManagerMode

@cmd2.with_default_category('MODE')
class CmdModeControl(cmd2.CommandSet):
    def __init__(self, parent: "TrackerManager"):
        self.parent: "TrackerManager" = parent
        super().__init__()

    def _list_modes(self) -> List[str]:
        return self.parent._list_modes()

    end_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(end_parser)
    def do_end(self, ns: argparse.Namespace):
        self.parent._do_end()

    mode_parser = cmd2.Cmd2ArgumentParser()
    mode_parser.add_argument('mode', choices_provider=_list_modes)

    @cmd2.with_argparser(mode_parser)
    def do_mode(self, ns: argparse.Namespace) -> Optional[bool]:
        if ns.mode is None:
            self.parent.do_help('mode')
        elif ns.mode in self.parent._mode_maps:
            self.parent._set_mode(ns.mode)
            # clazz: Type[ManagerMode] = self.parent._mode_maps[ns.mode]
            # mode: ManagerMode = clazz(ns.mode, self.parent, list(), dict())
            # self.parent._update_mode(mode)