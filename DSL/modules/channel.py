'''
module: channel
functions: add, remove

usage: channel (add/remove) <port - if remove>
'''


def add(*args, **kwargs):
    """
    Add a channel

    :param *args: N/A
    :param **kwargs: N/A
    """
    print("added another port")


def remove(port, *args, **kwargs):
    """
    Remove port, port

    :param port: port number/name to remove
    :param *args: N/A
    :param **kwargs: N/A
    """
    print("removed port {}".format(port))
