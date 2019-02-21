###############################################################################

import importlib
import sys

###############################################################################


def parse_command(source, gui_obj):
    """parse_command

    :param source:
    :param gui_obj:
    """
    line = source.strip()
    if not line or line[0] == '#':
        return
    parts = line.split()
    if parts[0] == 'exit':
        sys.exit(0)
    if parts[0] == 'help':
        if len(parts) == 1:
            get_help()
            print("Request for module to get help for")
            return
        else:
            for module in parts[1:]:
                get_help(module)
        return
    try:
        mod = importlib.import_module(parts[0])
    except ImportError:
        print("Command not found")
        return
    args, kwargs = get_args(parts[2:])
    dep_inj(kwargs, gui_obj)
    getattr(mod, parts[1])(*args, **kwargs)


###############################################################################
def get_args(dsl_args):
    """get_args

    :param dsl_args:
    """
    key_words = ['port', 'channel']
    args = []
    kwargs = {}
    skip = False
    for dsl_arg in dsl_args:
        if skip:
            args.append(dsl_arg)
            skip = False
            continue
        if '=' in dsl_arg:
            k, v = dsl_arg.split('=', 1)
            kwargs[k] = v
        elif dsl_arg in key_words:
            skip = True
            continue
        else:
            args.append(dsl_arg)
    return args, kwargs


###############################################################################


def get_help(module_name=None):
    """get_help

    :param module_name: module to get docs for {default: None}
    """
    if module_name:
        mod = importlib.import_module(module_name)
        print(mod.__doc__ or '')
        for name in dir(mod):
            if not name.startswith('_'):
                attr = getattr(mod, name)
                print(attr.__name__)
                print(attr.__doc__ or '', '\n')
    else:
        with open('./modules.txt', 'r') as mfile:
            for line in mfile.readlines():
                module_name = line.strip()
                mod = importlib.import_module(module_name)
                print(mod.__doc__ or '')
                for name in dir(mod):
                    if not name.startswith('_'):
                        attr = getattr(mod, name)
                        print(attr.__name__)
                        print(attr.__doc__ or '', '\n')


###############################################################################


def dep_inj(kwargs, gui_obj):
    if 'gui_obj' not in kwargs:
        kwargs['gui_obj'] = gui_obj


###############################################################################
