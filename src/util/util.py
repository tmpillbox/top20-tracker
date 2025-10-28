
import argparse
from datetime import datetime


class Utility:
    @staticmethod
    def str2bool(arg: str) -> bool:
        arg = arg.lower()
        if arg in [ 'yes', 'y', 'true', 't', '1' ]:
            return True
        elif arg in [ 'no', 'n', 'false', 'f', '0' ]:
            return False
        else:
            raise argparse.ArgumentTypeError("Invalid option, choose from: y, yes, t, true, n, no, f, false, 0, 1")


CALYEAR = datetime.now().year

