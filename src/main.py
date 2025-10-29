#!/usr/bin/env python3

import argparse

from typing import List

from src.tracker_manager import TrackerManager
from src.util.util import CALYEAR


def main(params: argparse.Namespace, args: List[str]) -> None:
    year = params.year
    if not year:
        year = CALYEAR
    interactive = None
    if params.interactive:
        interactive = True
    if params.no_interactive:
        interactive = False
    if interactive is None:
        interactive = not args
    
    votes_manager = TrackerManager(
        votes_file=params.votes_file,
        groupings_file=params.groupings_file,
        results_file=params.results_file,
        year=year,
        interactive=interactive
    )
    if interactive:
        votes_manager.cmdloop(TrackerManager.combobulate_line(args))
    else:
        votes_manager.onecmd(TrackerManager.combobulate_line(args))

