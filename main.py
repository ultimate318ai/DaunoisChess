import pygame
from display.displayMenu import draw_menu_home_page


def main():
    pygame.init()
    pygame.display.init()
    draw_menu_home_page()


if __name__ == '__main__':
    main()
