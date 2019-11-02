import sys


def except_hook(cls, exception, traceback):
    """Prints PyQt5 exceptions to the console."""
    print("*************** ERROR ***************", flush=True)
    sys.__excepthook__(cls, exception, traceback)
    sys.stderr.flush()
