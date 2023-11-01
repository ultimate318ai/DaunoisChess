"""
Custom exception used in chess context.
"""


class ChessException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return super(ChessException, self).__str__()
