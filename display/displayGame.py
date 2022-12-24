import chess
import chess.variant
import pygame
import chess.svg
from reportlab.graphics import renderPM

imported_cairosvg = True
try:
    from cairosvg import svg2png
except ImportError:
    imported_cairosvg = False
    from svglib.svglib import svg2rlg
from svglib.svglib import svg2rlg
from pygame_widgets.button import Button, ButtonArray
from typing import List, Tuple, Optional
from misc import map_pieces

last_move: chess.Move
MOOVES: List[chess.Move]
algebraic_moves: List[str] = []
draw_piece_mouse_cursor = False
piece_mouse_cursor: chess.Piece
from_index_draw_moves = 0
to_index_draw_move = 6

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def show(new_fen: str, board: chess.Board, screen: pygame.Surface, orientation_white=True, koth=False, rk=False,
         ch=False):
    global MOOVES, last_move, imported_cairosvg, draw_piece_mouse_cursor, piece_mouse_cursor, \
        from_index_draw_moves, to_index_draw_move

    screen.fill(WHITE)
    type_board = type(board)
    size_board = min(screen.get_size())

    if 'MOOVES' in globals():
        squares = [m.to_square for m in MOOVES]

    if board.is_check():
        for square in board.attacks(last_move.to_square):
            if board.piece_at(square):
                piece = board.piece_at(square)
                if (piece.piece_type == chess.KING or piece.piece_type == chess.AMAZON) and piece.color is board.turn:
                    king_square = square

    # draw chess board and pieces
    if imported_cairosvg:
        svg2png(bytestring=chess.svg.board(board=board,
                                           squares=squares if 'squares' in locals() else None,
                                           size=size_board,
                                           arrows=[chess.svg.Arrow(chess.D4, chess.D4),
                                                   chess.svg.Arrow(chess.E4, chess.E4),
                                                   chess.svg.Arrow(chess.D5, chess.D5),
                                                   chess.svg.Arrow(chess.E5, chess.E5)
                                                   ] if koth else [
                                               chess.svg.Arrow(chess.SQUARES[s], chess.SQUARES[s])
                                               for s in range(56, 64)
                                           ] if rk else [],
                                           lastmove=last_move if 'last_move' in globals() else None,
                                           check=king_square if 'king_square' in locals() else None,
                                           style='''
                                                .circle {
                                                stroke: #FFFF00;
                                                fill: #FFFF00;
                                                opacity: 0.2
                                                }
                                                ''' if koth or rk else None
                                           ,
                                           flipped=not orientation_white
                                           ),
                write_to='board.png')
    else:
        with open('../board.svg', "w") as svg_file:
            svg_file.write(chess.svg.board(board=board,
                                        squares=squares if 'squares' in locals() else None,
                                        size=size_board,
                                        arrows=[chess.svg.Arrow(chess.D4, chess.D4),
                                                chess.svg.Arrow(chess.E4, chess.E4),
                                                chess.svg.Arrow(chess.D5, chess.D5),
                                                chess.svg.Arrow(chess.E5, chess.E5)
                                                ] if koth else [
                                            chess.svg.Arrow(chess.SQUARES[s], chess.SQUARES[s])
                                            for s in range(56, 64)
                                        ] if rk else [],
                                        lastmove=last_move if 'last_move' in globals() else None,
                                        check=king_square if 'king_square' in locals() else None,
                                        style='''
                                                .circle {
                                                stroke: #FFFF00;
                                                fill: #FFFF00;
                                                opacity: 0.2
                                                } 
                                                ''' if koth or rk else None
                                        ))
        image = svg2rlg(f'../board.svg')
        renderPM.drawToFile(image, "board.png", fmt='PNG')
    screen.blit(pygame.image.load('./board.png'), (0, 0))
    if ch:
        draw_ch_pocket(screen, board, size_board)
        if draw_piece_mouse_cursor:
            draw_piece_on_mouse_cursor(screen, board, piece_mouse_cursor, size_board)
    draw_moves_board(screen, board, size_board, from_index_draw_moves, to_index_draw_move)


def draw_ch_pocket(screen: pygame.Surface, board: chess.variant.CrazyhouseBoard, board_size: int):
    """
    draw the widget used for the game, with the draw button, the cancel move one and the give up button
    """
    width, height = screen.get_size()

    cell_size = max(min(abs((width - 10 - board_size) // 10), abs(height // 10 - 10)), 1)
    pygame.draw.rect(screen, BLACK,
                     rect=pygame.Rect((board_size, height // 2 - 1, width - 1, height - 1)), width=5)

    images_str = ['pawn.png', "rook.png", 'queen.png', 'knight.png', 'bishop.png',
                  'Pawn.png', 'Rook.png', 'Queen.png', 'Knight.png', 'Bishop.png']

    texts = [str(board.pockets[chess.BLACK].count(piece_type=piece_t)) for piece_t in [1, 4, 5, 2, 3]] + \
            [str(board.pockets[chess.WHITE].count(piece_type=piece_t)) for piece_t in [1, 4, 5, 2, 3]]

    images_white = [pygame.transform.scale(pygame.image.load('pictures/{0}'.format(image)).convert_alpha(),
                                           (cell_size, cell_size))
                    for image in filter(lambda s: s[0].upper == s[0], images_str)]

    images_black = [pygame.transform.scale(pygame.image.load('pictures/{0}'.format(image)).convert_alpha(),
                                           (cell_size, cell_size))
                    for image in filter(lambda s: s[0].upper != s[0], images_str)]

    images = images_black + images_white

    crasyhouse_pocket = ButtonArray(screen, board_size, height // 2, (width - board_size) // 2, height // 2,
                                    shape=(2, 5), images=images, texts=texts, textHAligns=['right' for _ in range(10)])
    crasyhouse_pocket.draw()


def draw_moves_board(screen: pygame.Surface, board: chess.Board, board_size: int, from_index: int, to_index: int):
    """
    draw the list of the mooves in the game, the list can be modified by the user input
    """
    global algebraic_moves
    width, height = screen.get_size()

    pygame.draw.rect(screen, BLACK,
                     rect=pygame.Rect((board_size, 0, width - 1, height // 2 - 4)), width=5)

    texts = ["" for _ in range(6)]

    counter = 0
    bias = 0
    for index in range(min(from_index, len(board.move_stack)), min(to_index, len(board.move_stack))):
        texts[counter + bias] = algebraic_moves[index]
        counter += 2
        if counter == len(texts):
            counter = 0
            bias = 1 - bias
    moves_tab = ButtonArray(screen, board_size, 0, (width - board_size) // 2, height // 2,
                            shape=(3, 2), texts=texts)
    moves_tab.draw()


def affect_mooves(a):
    """
    #TODO : code clean and pretty
    """
    global MOOVES
    MOOVES = a


def affect_draw_piece_mouse_cursor(draw: bool, piece: Optional[chess.Piece]):
    """
    #TODO : code clean and pretty
    """
    global draw_piece_mouse_cursor, piece_mouse_cursor
    draw_piece_mouse_cursor = draw
    if piece:
        piece_mouse_cursor = piece


def affect_last_mooves(a):
    """
    #TODO : code clean and pretty
    """
    global last_move
    last_move = a


def increment_from_last_move(board: chess.Board):
    """
    draw the chess moves board
    """
    global from_index_draw_moves, to_index_draw_move
    if to_index_draw_move + 1 < len(board.move_stack):
        from_index_draw_moves += 1
        to_index_draw_move += 1


def decrement_from_last_move(board: chess.Board):
    """
    draw the chess moves board
    """
    global from_index_draw_moves, to_index_draw_move
    if from_index_draw_moves - 1 > 0:
        from_index_draw_moves -= 1
        to_index_draw_move -= 1


def add_move_in_algebric_list(move: chess.Move, board: chess.Board):
    """
    add the move in the list with the algebraic notation
    """
    global algebraic_moves
    algebraic_moves.append(board.lan(move))


def clear_globals_draw_game():
    """
    clear all the globals in display
    """
    global last_move, MOOVES, algebraic_moves, draw_piece_mouse_cursor, piece_mouse_cursor, \
        from_index_draw_moves, to_index_draw_move
    last_move = None
    MOOVES = []
    algebraic_moves = []
    draw_piece_mouse_cursor = False
    piece_mouse_cursor = None
    from_index_draw_moves = 0
    to_index_draw_move = 6


def draw_text(text: str, pos: Tuple[int, int], screen):
    """
    draw text #text on screen
    """
    if not pygame.font.get_init():
        pygame.font.init()
    my_font = pygame.font.SysFont('Comic Sans MS', 50)
    text_surface = my_font.render(text, False, (0, 0, 0))
    screen.blit(text_surface, pos)


def draw_piece_on_mouse_cursor(screen, board: chess.variant.CrazyhouseBoard, piece: chess.Piece, board_size: int):
    """
    draw a chess piece on the position of the mouse cursor
    if the cursor is in the window
    """
    width, height = screen.get_size()
    cell_size = max(min(abs((width - 10 - board_size) // 10), abs(height // 10 - 10)), 1)
    pos = pygame.mouse.get_pos()
    if board.pockets[piece.color].count(piece.piece_type) > 0:
        screen.blit(pygame.transform.scale(pygame.image.load('./pictures/{0}.png'.format(map_pieces[piece.symbol()])).
                                           convert_alpha(), (cell_size, cell_size)), pos)


def draw_end_game(screen: pygame.Surface, outcome: chess.Outcome):
    """
    draw the endgame status
    """
    width, height = screen.get_size()

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK,
                     rect=pygame.Rect((min(width, height) // 2, 0, width - 1, height // 2 - 4)), width=5)

    texts = [outcome.result(),
             "Game ended by Draw" if not outcome.winner else "white wins" if outcome.winner else "black wins"]
    moves_tab = ButtonArray(screen, min(width, height) // 2, 0, (width - min(width, height) // 2) // 2, height // 2,
                            shape=(2, 1), texts=texts)
    moves_tab.draw()
