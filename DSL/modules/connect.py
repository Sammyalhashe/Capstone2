'''
module: connect
functions: to

usage: connect to <port>
'''
def to(port, *args, **kwarg):
    """
    Connects to serial port, port
    :param port: port number/name to connect to
    :param *args: N/A
    :param **kwarg: N/A
    """
    print("Connected to port {}".format(port))
