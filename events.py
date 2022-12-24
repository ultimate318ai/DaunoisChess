import sys
import chess.variant
import pygame_widgets
from pygame import *
from misc import *
from chess import *
from display.displayGame import affect_mooves, affect_last_mooves, affect_draw_piece_mouse_cursor, \
    increment_from_last_move, decrement_from_last_move, add_move_in_algebric_list
import chess.engine
from ChessException import ChessException

stockfish_loaded = True
try:
    import stockfish
except ImportError:
    stockfish = None
    stockfish_loaded = False

selected_piece: chess.Piece
selected_piece_case: chess.Square
piece_on_mouse_cursor: chess.Piece
total_moves = []
counter_mooves = 0
engine: chess.engine.SimpleEngine
variant_engine: stockfish.Stockfish if stockfish else None
is_game_over_special_variant = False

is_turn_IA = False
is_stockfish_init = False

stockfish_settings = {
    "Threads": 1,
    "Hash": 16,
    "Skill Level": 20
}

stockfish_variant_settings = {
    "Threads": 1,
    "Hash": 16,
    "Skill Level": 20,
    "VariantPath": "IA/Fairy-Stockfish/src/variants.ini",
    "UCI_Variant": "maharajah",
}


def clear_globals_events():
    global selected_piece, selected_piece_case, total_moves, counter_mooves, engine, is_stockfish_init, is_turn_IA,\
        variant_engine
    selected_piece = None
    selected_piece_case = None
    total_moves = []
    counter_mooves = 0
    engine = None
    variant_engine = None
    is_turn_IA = False
    is_stockfish_init = False


def init_stockfish_engine(**kargs):
    """

    """
    global engine
    find_ia_path("stockfish")
    with open('./ia_setting.dchess', "r") as file_path_ia:
        for line in file_path_ia.readlines():
            try:
                engine = chess.engine.SimpleEngine.popen_uci(line)
            except NameError:
                continue

    for key, value in kargs.items():
        if key in stockfish_settings.keys():
            stockfish_settings[key] = value
        elif key == "difficulty":
            stockfish_settings["Skill Level"] = value

    engine.configure(options=stockfish_settings)


def init_variant_engine(**kargs):
    """
    """
    global variant_engine
    find_ia_path("stockfish")
    with open('./ia_setting.dchess', "r") as file_path_ia:

        for key, value in kargs.items():
            if key in stockfish_variant_settings.keys():
                stockfish_variant_settings[key] = value
            elif key == "difficulty":
                stockfish_variant_settings["Skill Level"] = value
        for line in file_path_ia.readlines():
            try:
                variant_engine = stockfish.Stockfish(line, parameters=stockfish_variant_settings)
            except NameError:
                continue


def manage_events(board: Board, screen: pygame.Surface, is_opponent_bot=False, is_orientation_board_white=True,
                  difficulty=20):
    """
    function used for all the events of pygame
    """
    global selected_piece, counter_mooves, total_moves, is_turn_IA, is_stockfish_init, selected_piece_case,\
        piece_on_mouse_cursor, variant_engine, is_game_over_special_variant, stockfish_loaded

    if not is_stockfish_init:
        is_turn_IA = is_opponent_bot and not is_orientation_board_white
        if is_board_extra_variant(board):
            if not stockfish_loaded:
                raise ChessException()
            init_variant_engine(difficulty=difficulty)
            variant_engine.set_fen_position(board.fen())
        else:
            init_stockfish_engine(difficulty=difficulty)
        is_stockfish_init = True

    if is_turn_IA:

        if is_board_extra_variant(board):
            m = variant_engine.get_best_move()
            if m is None:
                is_game_over_special_variant = True
                return
            ia_play = chess.Move.from_uci(m)
            variant_engine.make_moves_from_current_position([ia_play.uci()])
        else:
            ia_play = engine.play(board, limit=chess.engine.Limit(0.3)).move

        selected_piece = board.piece_at(ia_play.from_square)
        selected_piece_case = ia_play.to_square
        if isinstance(board, chess.variant.CrazyhouseBoard):
            if board.is_capture(ia_play):
                piece_taken = board.piece_at(ia_play.to_square)
                board.pockets[selected_piece.color].add(piece_taken)
        add_move_in_algebric_list(ia_play, board)
        board.push(ia_play)
        is_turn_IA = False
        total_moves.append(ia_play)
        affect_last_mooves(ia_play)
        counter_mooves += 1
        affect_mooves([])
        return

    events = pygame.event.get()
    pygame_widgets.update(events)
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            if 'engine' in globals():
                engine.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                raise ChessException()
            if isinstance(board, chess.variant.CrazyhouseBoard) \
                    and any([check_pokets_non_empty(board, chess.Piece(type_p, board.turn))
                             for type_p in chess.PIECE_TYPES]):
                if event.key == K_q:
                    piece_on_mouse_cursor = Piece.from_symbol('Q' if board.turn else 'q')
                    affect_draw_piece_mouse_cursor(draw=True, piece=piece_on_mouse_cursor
                                                   )
                elif event.key == K_p:
                    piece_on_mouse_cursor = Piece.from_symbol('P' if board.turn else 'p')
                    affect_draw_piece_mouse_cursor(draw=True, piece=piece_on_mouse_cursor
                                                   )
                elif event.key == K_k:
                    piece_on_mouse_cursor = Piece.from_symbol('N' if board.turn else 'n')
                    affect_draw_piece_mouse_cursor(draw=True, piece=piece_on_mouse_cursor
                                                   )
                elif event.key == K_r:
                    piece_on_mouse_cursor = Piece.from_symbol('R' if board.turn else 'r')
                    affect_draw_piece_mouse_cursor(draw=True, piece=piece_on_mouse_cursor
                                                   )
                elif event.key == K_b:
                    piece_on_mouse_cursor = Piece.from_symbol('B' if board.turn else 'b')
                    affect_draw_piece_mouse_cursor(draw=True, piece=piece_on_mouse_cursor
                                                   )
                else:
                    affect_draw_piece_mouse_cursor(draw=False, piece=None)
            if event.key == K_UP:
                increment_from_last_move(board)
            elif event.key == K_DOWN:
                decrement_from_last_move(board)

        elif event.type == MOUSEMOTION:

            if 'piece_on_mouse_cursor' in globals() and piece_on_mouse_cursor is not None:  # ch drop move
                pos = mouse.get_pos()
                square = convert_int_pos_to_chess_square(pos[0], pos[1], screen)
                if square is not None:
                    piece_on_mouse = board.piece_at(square)
                    pseudo_move = Move(square, square, drop=piece_on_mouse_cursor.piece_type)
                    if not piece_on_mouse and check_pokets_non_empty(board, piece_on_mouse_cursor) and \
                            is_drop_valid(pseudo_move, board):
                        affect_mooves([pseudo_move])

        elif event.type == MOUSEBUTTONDOWN:

            try:
                if event.button == 4 and (0, 0) <= mouse.get_pos() <= (min(screen.get_size()), min(screen.get_size())) \
                        and counter_mooves < len(total_moves):
                    new_move = total_moves[counter_mooves]
                    board.push(new_move)
                    counter_mooves += 1
                if event.button == 5 and (0, 0) <= mouse.get_pos() <= (min(screen.get_size()), min(screen.get_size())) \
                        and counter_mooves > 0:
                    counter_mooves -= 1
                    board.pop()
            except IndexError:
                pass
            else:
                mouse_buttons = mouse.get_pressed(num_buttons=3)

                if mouse_buttons[0] and not is_turn_IA:  # Selection of a piece

                    if 'piece_on_mouse_cursor' in globals() and piece_on_mouse_cursor is not None: # ch drop move
                        pos = mouse.get_pos()
                        square = convert_int_pos_to_chess_square(pos[0], pos[1], screen)
                        if square is not None:
                            piece_on_mouse = board.piece_at(square)
                            if counter_mooves == len(total_moves)\
                                    and piece_on_mouse is None and check_pokets_non_empty(board, piece_on_mouse_cursor):
                                # do a drop moove ? not on a piece and if possible
                                is_promotion = is_move_a_promotion(selected_piece, Move(selected_piece_case, square))
                                pseudo_move = Move(square, square, drop=piece_on_mouse_cursor.piece_type,
                                                   promotion=chess.QUEEN if is_promotion else None)
                                try:
                                    if is_drop_valid(pseudo_move, board):
                                        add_move_in_algebric_list(pseudo_move, board)
                                        board.push(pseudo_move)
                                        is_turn_IA = is_opponent_bot
                                        total_moves.append(pseudo_move)
                                        counter_mooves += 1
                                        affect_last_mooves(pseudo_move)
                                        affect_mooves([])
                                        piece_on_mouse_cursor = None
                                        affect_draw_piece_mouse_cursor(draw=False, piece=None)
                                except ValueError:
                                    piece_on_mouse_cursor = None
                                    affect_draw_piece_mouse_cursor(draw=False, piece=None)
                                    return
                                except KeyError:
                                    piece_on_mouse_cursor = None
                                    affect_draw_piece_mouse_cursor(draw=False, piece=None)
                                    return
                    else:
                        piece_on_mouse_cursor = None
                        affect_draw_piece_mouse_cursor(draw=False, piece=None)
                        if 'selected_piece' not in globals():
                            selected_piece = None

                        pos = mouse.get_pos()
                        case = convert_int_pos_to_chess_square(pos[0], pos[1], screen)

                        if case is not None:
                            piece_on_mouse = board.piece_at(case)
                            #print("piece on mouse : ", piece_on_mouse)

                            if selected_piece is not None and counter_mooves == len(total_moves):  # do a moove ?
                                selected_piece_moves = get_piece_legal_moves(selected_piece, board, selected_piece_case)
                                is_promotion = is_move_a_promotion(selected_piece, Move(selected_piece_case, case))
                                pseudo_move = Move(selected_piece_case, case,
                                                   promotion=chess.QUEEN if is_promotion else None)
                                if is_move_in_mooves(pseudo_move, selected_piece_moves):
                                    if isinstance(board, chess.variant.CrazyhouseBoard):
                                        if board.is_capture(pseudo_move):
                                            if board.is_en_passant(pseudo_move):
                                                piece_taken = board.piece_at(pseudo_move.to_square + (8
                                                                             if selected_piece.color else -8))
                                            else:
                                                piece_taken = board.piece_at(pseudo_move.to_square)
                                            board.pockets[selected_piece.color].add(piece_taken)
                                    add_move_in_algebric_list(pseudo_move, board)
                                    board.push(pseudo_move)
                                    if 'variant_engine' in globals() and variant_engine is not None:
                                        m = variant_engine.get_best_move()
                                        if m is None:
                                            is_game_over_special_variant = True #TODO: fix that
                                            return
                                        variant_engine.make_moves_from_current_position([pseudo_move.uci()])
                                    is_turn_IA = is_opponent_bot
                                    total_moves.append(pseudo_move)
                                    counter_mooves += 1
                                    affect_last_mooves(pseudo_move)
                                    affect_mooves([])
                                    return

                            selected_piece = None
                            if piece_on_mouse is not None and counter_mooves == len(total_moves):
                                selected_piece = piece_on_mouse
                                selected_piece_case = case
                                #print("piece selected & case:", selected_piece, " ",case)
                                affect_mooves(get_piece_legal_moves(piece_on_mouse, board, case))
