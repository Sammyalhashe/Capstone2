###############################################################################

import code
import sys
from sys import stderr
from main_helpers import parse_command


###############################################################################
class Console(object):
    """Console"""
    ps1 = '> '
    ps2 = '. '

    def __init__(self, gui_obj):
        """__init__

        :param gui_obj:
        """
        self.gui_obj = gui_obj

    def run(self, fd):
        """run

        :param fd:
        """
        for line in fd:
            print(line)

    def interact(self, locals=None):
        """interact

        :param locals:
        """

        class LambdaConsole(code.InteractiveConsole):
            """LambdaConsole"""

            def runsource(code_console, source, filename=None, symbol=None):
                """runsource

                :param code_console:
                :param source:
                :param filename:
                :param symbol:
                """
                # Return True if more input needed, else False.
                try:
                    print(source)
                    parse_command(source, self.gui_obj)
                except SystemExit:
                    raise
                return False

        # import readline to support line editing within console session.
        try:
            import readline
            readline
        except ImportError:
            pass

        # Patch ps1 & ps2 for interaction. Note sys.psX may be unset.
        ps1, ps2 = getattr(sys, 'ps1', None), getattr(sys, 'ps2', None)
        try:
            sys.ps1, sys.ps2 = self.ps1, self.ps2
            LambdaConsole(locals=locals).interact(banner='')
        finally:
            sys.ps1, sys.ps2 = ps1, ps2

    def run_in_main(self, fd=None, interact=False):
        """run_in_main

        :param fd:
        :param interact:
        """
        if fd is None:
            fd = sys.stdin
        if fd.isatty():
            self.interact()
        else:
            try:
                self.run(fd=fd)
            except Exception as err:
                print(err, file=stderr)
                return 1
        return 0


###############################################################################


def main(gui_obj, fd=None):
    """main

    :param gui_obj:
    :param fd:
    """
    """main

    :param gui_obj:
    :param fd:
    """
    return Console(gui_obj).run_in_main(fd)


###############################################################################

if __name__ == '__main__':
    sys.exit(main())
###############################################################################
