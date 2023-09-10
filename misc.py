from extra_variant import AmazonChessBoard
import pygame
import os
from chess import *
import chess.variant
from typing import List, Optional

orientation_board = True  # True if the board is white oriented, else False
engine_path: str
PIECE = 0
POS = 1
IS_DRAWABLE = 2

map_pieces = {
    "k": "king",
    "K": "King",
    "Q": "Queen",
    "q": "queen",
    "p": "pawn",
    "P": "Pawn",
    "n": "knight",
    "N": "Knight",
    "B": "Bishop",
    "b": "bishop",
    "R": "Rook",
    "r": "rook",
}

map_pieces_types = {
    "k": chess.KING,
    "K": chess.KING,
    "Q": chess.QUEEN,
    "q": chess.QUEEN,
    "p": chess.PAWN,
    "P": chess.PAWN,
    "n": chess.KNIGHT,
    "N": chess.KNIGHT,
    "B": chess.BISHOP,
    "b": chess.BISHOP,
    "R": chess.ROOK,
    "r": chess.ROOK,
}

NORMAL_BOARD_SIZE = 8
LETTER_A_CODE = 97


def set_orientation_board(a):
    """ """
    global orientation_board
    orientation_board = a


def get_orientation_board():
    """ """
    global orientation_board
    return orientation_board


def convert_int_pos_to_chess_square(
    pos_abs: int, pos_ord: int, screen: pygame.surface.Surface
) -> Optional[chess.Square]:
    """
    used to return the square pointed with the mouse
    piece_at(square: chess.Square) → Optional[chess.Piece]
    """

    def reverse_pos(position: str) -> str:
        """
        rverse the position string given
        """
        if len(position) != 2:
            return position

        mapping_table_letter = {
            "a": "h",
            "b": "g",
            "c": "f",
            "d": "e",
            "e": "d",
            "f": "c",
            "g": "b",
            "h": "a",
        }
        # print("case d'origine:", position)
        # print("case mappée : ",mapping_table_letter[position[0]] + str(8 - (int(position[1]) - 1)))
        return mapping_table_letter[position[0]] + str(8 - (int(position[1]) - 1))

    dimension = min(screen.get_size())
    square_size = 2 * dimension // 17

    if 0 <= pos_abs <= dimension and 0 <= pos_ord <= dimension:
        letter = chr(pos_abs // square_size + LETTER_A_CODE)
        number = max(NORMAL_BOARD_SIZE - pos_ord // square_size, 1)
        letter_pos = str(letter) + str(number)
        return (
            parse_square(letter_pos)
            if orientation_board
            else parse_square(reverse_pos(letter_pos))
        )
    return None


def get_piece_legal_moves(
    piece: chess.Piece, board: Board, pos_piece: chess.Square
) -> List[chess.Move]:
    """
    print for a piece given the legal moves possible
    """

    global orientation_board

    def get_piece_mooves(_piece: chess.Piece, _pos_piece: chess.Square) -> list:
        """
        #return all the moves of a #piece
        #TODO: other pieces + promotion + inversed chessboard
        """
        mooves = []
        value = 8

        condition_white = _pos_piece <= 15
        condition_black = _pos_piece >= 48

        if _piece.piece_type == chess.PAWN:
            try:
                if _piece.color == chess.WHITE:
                    if condition_white:  # pawn haven't moved yet and can take piece
                        mooves.append(
                            chess.Move(_pos_piece, chess.SQUARES[_pos_piece + value])
                        )
                        mooves.append(
                            chess.Move(
                                _pos_piece, chess.SQUARES[_pos_piece + 2 * value]
                            )
                        )
                    else:
                        mooves.append(
                            chess.Move(_pos_piece, chess.SQUARES[_pos_piece + value])
                        )
                else:
                    if condition_black:  # pawn haven't moved yet
                        mooves.append(
                            chess.Move(_pos_piece, chess.SQUARES[_pos_piece - value])
                        )
                        mooves.append(
                            chess.Move(
                                _pos_piece, chess.SQUARES[_pos_piece - 2 * value]
                            )
                        )
                    else:
                        mooves.append(
                            chess.Move(_pos_piece, chess.SQUARES[_pos_piece - value])
                        )
            except IndexError as e:
                print("bad value :", e.args)
        elif _piece.piece_type == chess.KING:
            for pseudo_move in board.pseudo_legal_moves:
                if board.has_kingside_castling_rights(
                    _piece.color
                ) and board.is_kingside_castling(pseudo_move):
                    mooves.append(pseudo_move)
                elif board.has_queenside_castling_rights(
                    _piece.color
                ) and board.is_queenside_castling(pseudo_move):
                    mooves.append(pseudo_move)

        for _square_attacked in get_attacked_squares_from_square(board, _pos_piece):
            mooves.append(Move(_pos_piece, _square_attacked))
        return mooves

    def get_piece_legal_mooves(moves: List[chess.Move]) -> List[chess.Move]:
        """
        from a list of moves, keep only the legal ones
        """
        legal_moves = []
        for m in moves:
            try:
                board.find_move(m.from_square, m.to_square, m.promotion)
                legal_moves.append(m)
            except ValueError:
                continue
        return legal_moves

    return (
        get_piece_legal_mooves(get_piece_mooves(piece, pos_piece))
        if piece is not None
        else []
    )


def is_eq_mooves(move1: Move, move2: Move) -> bool:
    """
    compare the two moves using their uci notations
    """
    return move1.uci() == move2.uci() or move1.uci() == move2.uci() + "q"


def is_move_in_mooves(move: Move, tab: List[Move]) -> bool:
    """
    check if the move is in the tab list
    #param move: the move considered
    #param tab: the list of moves
    #return true if move is in tab, false otherwise
    """
    for m in tab:
        if is_eq_mooves(move, m):
            return True
    return False


def get_attacked_squares_from_square(
    board: chess.Board, _square: chess.Square
) -> chess.SquareSet:
    """
    #return the set of square of attacked pieces
    """
    return board.attacks(_square)


def is_square_promotion_square(_square: chess.Square) -> bool:
    """
    #return if the square #_square given might be a promotion square
    """
    return 0 <= _square <= 7 or 56 <= _square <= 63


def is_move_a_promotion(piece: chess.Piece, move: chess.Move) -> bool:
    """
    #return is a chess move might be a promotion one
    """
    return piece.piece_type == chess.PAWN and is_square_promotion_square(move.to_square)


def game_is_finished(board: chess.Board) -> bool:
    """
    #return is a game is finished
    """
    type_b = type(board)

    if type_b == chess.Board:
        if board.is_checkmate():
            return True
    return board.is_variant_end()


def find_ia_path(target: str, path="", sep="/", n=0):
    """
    find recursively the path of the IA engine
    return path when found else nothing
    """
    global engine_path

    if path == "":
        path = os.getcwd()
    list_files_only = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    ]
    list_dir_only = [
        d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))
    ]

    for f in list_files_only:
        if f == target:
            engine_path = path + sep + f
            with open("./ia_setting.dchess", "w+") as file:
                file.write(engine_path)
            return

    for d in list_dir_only:
        _path = path + sep + d
        find_ia_path(target, path=_path, sep=sep, n=n + 1)
        _path = ""


def check_pokets_non_empty(
    board: chess.variant.CrazyhouseBoard, piece: chess.Piece
) -> bool:
    """
    #return if the piece type is contained in the pocket of the player given
    """
    return board.pockets[board.turn].count(piece.piece_type) > 0


def is_drop_valid(move: chess.Move, board: chess.variant.CrazyhouseBoard) -> bool:
    """
    return if the drop can be validated of not
    """
    b = board.copy()
    try:
        b.push(move)
        b.push(chess.Move.null())  # put turn on white side
        return not b.is_check()
    except ValueError:
        return False


def is_board_extra_variant(board: chess.Board) -> bool:
    """
    #return true of the board is one on the variants not
    managed by chess python engine
    """
    return type(board) == AmazonChessBoard
