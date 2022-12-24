import random
import extra_variant
import pygame
import pygame_menu
import pyautogui
import chess.variant
from chess import *
from display.displayGame import show, draw_end_game, clear_globals_draw_game
from events import manage_events, clear_globals_events, is_game_over_special_variant
from misc import set_orientation_board, get_orientation_board
from ChessException import ChessException

is_opponent_bot = False  # use it for the bot level
# if we wants to quit
is_game_resumed = False
is_board_init = False
difficulty = 0
DISPLAY_SURF = None
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
game_type = 1
fen_test1 = "8/8/8/8/4QK2/8/8/8 w - - 0 1"
fen = STARTING_FEN
fen_text_box: pygame_menu.widgets.widget.textinput.TextInput


def set_game_type(value, _game_type):
    """
    """
    global game_type, fen, fen_text_box
    # print("game type ", value[0][0])
    game_type = _game_type
    if game_type == 6:  # racing king
        fen = chess.variant.RacingKingsBoard.starting_fen
        if 'fen_text_box' in globals():
            fen_text_box.set_value(fen)
    elif game_type == 7:  # Horde
        fen = chess.variant.HordeBoard.starting_fen
        if 'fen_text_box' in globals():
            fen_text_box.set_value(fen)
    elif game_type == 10: # Amazon
        fen = extra_variant.AmazonChessBoard.starting_fen
        if 'fen_text_box' in globals():
            fen_text_box.set_value(fen)
    else:
        fen = STARTING_FEN
        if 'fen_text_box' in globals():
            fen_text_box.set_value(fen)


def set_opponent_type(value, opponent):
    choice = value[0][0]

    global is_opponent_bot
    if choice == 'play with bot':
        is_opponent_bot = True


def player_color(value, ballec):
    choice = value[0][0]

    if not (choice == 'white'):
        set_orientation_board(False)


def set_difficulty(value, _difficulty):
    """

    """
    global difficulty
    difficulty = _difficulty


def set_fen(value):
    global fen
    fen = value
    # print(fen)


def start_the_game_menu(menu: pygame_menu.menu.Menu, screen: pygame.Surface):
    # Do the job here !

    global fen, fen_text_box
    menu.clear()
    menu.add.selector('GameType', [('Chess', 1),
                                   ('Atomic', 2),
                                   ('Antichess', 3),
                                   ('Tree_check', 4),
                                   ('King of the hill', 5),
                                   ('Racing Kings', 6),
                                   ('Horde', 7),
                                   ('Crazyhouse', 8),
                                   ('Chess960', 9),
                                   ('Shatranj', 10)],
                      onchange=set_game_type)
    menu.add.selector('GameWith', [('play with friend', 1),
                                   ('play with bot', 2)],
                      onchange=set_opponent_type)
    menu.add.selector('difficulty', [('None', 0),
                                     ('Easiest', 2),
                                     ('Easy', 4),
                                     ('Standard', 6),
                                     ('Medium', 8),
                                     ('Medium+', 10),
                                     ('Hard', 12),
                                     ('Hard+', 14),
                                     ('Hardest', 16),
                                     ('Magnus', 18),
                                     ('Impossible', 20)],
                      onchange=set_difficulty)
    menu.add.selector('Game Orientation', [('white', 1),
                                           ('black', 1)],
                      onchange=player_color)
    fen_text_box = menu.add.text_input('From fen: ',
                                       default=fen,
                                       onchange=set_fen)
    menu.add.button("------------------------------------")
    menu.add.button('Start Game', start_the_game, screen, menu)

    # print(fen_text_box)


def start_the_game(screen: pygame.Surface, menu: pygame_menu.menu.Menu, resume_fen=STARTING_FEN):
    def init_board(variant_type: int, _fen, orientation: bool) -> chess.Board:
        """
        init the board with the param difficulty given. Default is 1 => standard
        """
        nonlocal koth, rk, ch

        try:
            if variant_type == 1:
                return Board(fen=_fen)
            elif variant_type == 2:
                return chess.variant.AtomicBoard(fen=_fen)
            elif variant_type == 3:
                return chess.variant.AntichessBoard(fen=_fen)
            elif variant_type == 4:
                return chess.variant.ThreeCheckBoard(fen=_fen)
            elif variant_type == 5:
                koth = True
                return chess.variant.KingOfTheHillBoard(fen=_fen)
            elif variant_type == 6:
                rk = True
                return chess.variant.RacingKingsBoard(fen=_fen)
            elif variant_type == 7:
                return chess.variant.HordeBoard(fen=_fen)
            elif variant_type == 8:
                ch = True
                return chess.variant.CrazyhouseBoard(fen=_fen)
            elif variant_type == 9:
                if _fen != STARTING_FEN:
                    return Board(fen=_fen, chess960=True)
                b = Board(chess960=True)
                b.set_chess960_pos(random.randint(0, 959))
                return b
            elif variant_type == 10:
                return extra_variant.AmazonChessBoard(fen=_fen)
            else:
                return Board(fen=_fen)
        except ValueError:
            if variant_type == 1:
                return Board(fen=STARTING_FEN)
            elif variant_type == 2:
                return chess.variant.AtomicBoard(fen=STARTING_FEN)
            elif variant_type == 3:
                return chess.variant.AntichessBoard(fen=STARTING_FEN)
            elif variant_type == 4:
                return chess.variant.ThreeCheckBoard(fen=STARTING_FEN)
            elif variant_type == 5:
                koth = True
                return chess.variant.KingOfTheHillBoard(fen=STARTING_FEN)
            elif variant_type == 6:
                rk = True
                return chess.variant.RacingKingsBoard(fen=chess.variant.RacingKingsBoard.starting_fen)
            elif variant_type == 7:
                return chess.variant.HordeBoard(fen=chess.variant.HordeBoard.starting_fen)
            elif variant_type == 8:
                ch = True
                return chess.variant.CrazyhouseBoard(fen=chess.variant.CrazyhouseBoard.starting_fen)
            elif variant_type == 9:
                b = Board(chess960=True)
                b.set_chess960_pos(random.randint(0, 959))
                return b
            elif variant_type == 10:
                return extra_variant.AmazonChessBoard(fen=extra_variant.AmazonChessBoard.starting_fen)
            else:
                return Board(fen=_fen)

    global is_opponent_bot, difficulty, game_type, fen, is_game_resumed

    koth = False
    rk = False
    ch = False
    menu.clear()
    screen.fill(WHITE)
    chess_b = init_board(game_type, _fen=fen, orientation=get_orientation_board()) if not is_game_resumed else init_board(game_type, _fen=resume_fen, orientation=get_orientation_board())
    while not (chess_b.is_game_over() or is_game_over_special_variant):
        try:
            manage_events(chess_b, screen, is_opponent_bot, get_orientation_board(), difficulty)
            show(new_fen=chess_b.fen(), board=chess_b, screen=screen, orientation_white=get_orientation_board(), koth=koth, rk=rk, ch=ch)
            pygame.display.update()
        except ChessException:
            screen.fill(WHITE)
            print_the_in_game_menu(screen, chess_b.fen())
    quit = False
    while not quit:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                quit = True
        draw_end_game(screen, chess_b.outcome())

    clear_globals_events()
    clear_globals_draw_game()
    draw_menu_home_page()


def draw_menu_home_page():
    """

    """
    global DISPLAY_SURF, fen
    fen = STARTING_FEN

    if DISPLAY_SURF is None:
        DISPLAY_SURF = pygame.display.set_mode(pyautogui.size(), pygame.RESIZABLE)
        DISPLAY_SURF.fill(WHITE)
    width, height = DISPLAY_SURF.get_size()
    menu = pygame_menu.Menu('Welcome', width, height,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.vertical_margin(20)
    menu.add.image("./pictures/acceuil.png")
    # menu.add.color_input("test", 'rgb')
    # menu.add.text_input('Name :', default='Un jeu par Nathan DAUNOIS')
    # menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
    menu.add.button('Play', start_the_game_menu, menu, DISPLAY_SURF)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(DISPLAY_SURF)


def print_the_in_game_menu(screen: pygame.surface.Surface, actual_fen: str):
    """
    print the menu in game with resume and quit button and
    other stuffs
    """
    width, height = screen.get_size()
    menu = pygame_menu.Menu('Welcome', width, height,
                            theme=pygame_menu.themes.THEME_BLUE)
    menu.add.button('Resume', resume_game, screen, menu, actual_fen)
    menu.add.button('Quit Game', quit_game, menu)
    menu.mainloop(screen)


def resume_game(screen: pygame.Surface, menu: pygame_menu.menu.Menu, actual_fen: str):
    """

    """
    global is_game_resumed
    menu.clear()
    is_game_resumed = True
    start_the_game(screen, menu, actual_fen)


def quit_game(menu: pygame_menu.menu.Menu):
    """

    """
    global is_game_resumed
    menu.clear()
    is_game_resumed = False
    clear_globals_events()
    clear_globals_draw_game()
    draw_menu_home_page()
