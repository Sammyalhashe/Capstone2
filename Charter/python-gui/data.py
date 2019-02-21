import zerorpc
from random import random
from rx.subjects import Subject


class dataRPC():
    """dataRPC"""

    def __init__(self):
        self.stream = None

    def getData(self, channels="1"):
        """getData

        :param channels: channels connected to
        """
        channels = channels.split(' ')
        return [random() for i in channels], [i for i in channels]

    def getStream(self):
        if not self.stream:
            print("Activate the Data Stream first")
            return None
        print(type(self.stream))
        return self.stream

    def activateStream(self):
        if not self.stream:
            self.stream = Subject()

    def getData_s(self, channels="1"):
        if not self.stream:
            self.activateStream()
        channels = channels.split(' ')
        self.stream.on_next([random() for i in channels])

    def getData_test(self):
        for i in range(25):
            self.getData_s()

    @zerorpc.stream
    def dataStream(self, channels="1"):
        channels = channels.split(' ')
        return [random() for i in channels]
