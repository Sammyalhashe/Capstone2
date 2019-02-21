###############################################################################

import sys
import console
from main_helpers import parse_command

###############################################################################
gui_obj = None

sys.path.insert(
    0, '/Users/sammyalhashemi/OneDrive/Year_4/Capstone/Code/DSL/modules')

# we read the dsl file
if len(sys.argv) == 2:
    with open(sys.argv[1], 'r') as file:
        for line in file:
            parse_command(line, gui_obj)
else:
    console.main(gui_obj)
###############################################################################
