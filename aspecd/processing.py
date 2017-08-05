"""Processing."""


class ProcessingStep:

    def __init__(self):
        self.undoable = False
        self.name = self.__class__.__name__
        self.parameters = dict()
