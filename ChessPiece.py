"""
class used for Piece storage
"""
import chess
import pygame
from typing import Tuple

id_piece_num = 0


class Position:
    """

    """
    def __init__(self, x: int, y: int) -> None:
        self.abs = x
        self.ord = y

    def __str__(self) -> str:
        return "({0},{1})".format(self.abs, self.ord)

    def __add__(self, other):
        if not isinstance(other, Position):
            return self
        return Position(self.abs+other.abs, self.ord+other.ord)

    def __sub__(self, other):
        if not isinstance(other, Position):
            return self
        return Position(self.abs-other.abs, self.ord-other.ord)

    def __mul__(self, other):
        if not isinstance(other, Position):
            return self
        return Position(self.abs * other.abs, self.ord * other.ord)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.abs == other.abs and self.ord == other.ord

    def set_values(self, _abs: int, _ord: int):
        self.abs = _abs
        self.ord = _ord

    def to_tuple(self) -> Tuple[int, int]:
        return self.abs, self.ord


class ChessPiece:
    """

    """

    def __init__(self, name: str,  surface, square: chess.Square,
                 is_drawable=True, _type=None, color=None):
        global id_piece_num
        self.id = id_piece_num
        id_piece_num += 1
        self.name = name
        self.surface = surface
        self.square = square
        self.is_drawable = is_drawable
        self.type = _type
        self.color = color

    def __str__(self) -> str:
        return "({0}, {1}, {2}, {3}, {4})".format(self.id, self.name, self.square, self.type, self.color)

    def __eq__(self, other):
        return isinstance(other, ChessPiece) and other.id == self.id and other.name == self.name

    def draw(self, screen, row, col):
        if self.is_drawable:
            screen.blit(self.surface, Position(row, col).to_tuple())


class ChessBoard(ChessPiece):
    """

    """
    def __init__(self, name: str, surface, is_drawable=True):
        super(ChessBoard, self).__init__(name, surface, is_drawable)

    def draw(self, screen, row=0, col=0):
        super(ChessBoard, self).draw(screen, row, col)
