import os
import sys
import threading
import time

from pynput import keyboard
import termios
import tty


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"
import pygame


from screen import Screen
from player import TronBot, TronPlayer


GAME_WIDTH = 75
GAME_HEIGHT = 75
SPEED = 10


class TronGame:
    def __init__(
        self,
        game_width: int,
        game_height: int,
        allow_keyboard=True,
        allow_joystick=True,
    ):
        self.screen = Screen(game_width, game_height)
        self.screen.clear_terminal()
        self.allow_keyboard = allow_keyboard
        self.allow_joystick = allow_joystick

        result = self.screen.ask_multiple_choice(
            "Welcome to Tron Tronerminal Game! Choose game mode: ",
            ["Player vs Player", "Player vs Bot", "Bot vs Bot"],
        )

        match result:
            case 0:
                self.player1 = TronPlayer("Player 1", "red")
                self.player2 = TronPlayer("Player 2", "cyan")
            case 1:
                self.player1 = TronPlayer("Player 1", "red")
                self.player2 = TronBot("Player 2", "cyan")
            case 2:
                self.player1 = TronBot("Player 1", "red")
                self.player2 = TronBot("Player 2", "cyan")

        height_half = self.screen.height // 2
        width_div = self.screen.width // 4
        self.player1.head = (width_div, height_half)
        self.player2.head = (3 * width_div, height_half)
        self.player2.dir = "left"

        self.game_over = False

        if allow_joystick:
            self.joysticks = []
            self.init_joysticks()

        self.screen.clear_terminal()
        self.print_board()

    def init_joysticks(self):

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.joysticks.append(joystick)
        else:
            self.joysticks = []

    def print_board(self):
        for i in range(self.screen.height):
            self.screen.print_on_coordinate(0, i, "|", "white")
            self.screen.print_on_coordinate(self.screen.width - 1, i, "|", "white")

        for j in range(self.screen.width):
            self.screen.print_on_coordinate(j, 0, "_", "white")
            self.screen.print_on_coordinate(j, self.screen.height - 1, "-", "white")

    def update_joystick_input(self, joystick, player):
        if not player.is_manully_controlled():
            return

        pygame.event.pump()

        hat_x, hat_y = 0, 0
        try:
            if joystick.get_numhats() > 0:
                hat_x, hat_y = joystick.get_hat(0)
        except pygame.error:
            pass

        if hat_y == 1 and player.dir != "down":
            player.dir = "up"
        elif hat_y == -1 and player.dir != "up":
            player.dir = "down"
        elif hat_x == -1 and player.dir != "right":
            player.dir = "left"
        elif hat_x == 1 and player.dir != "left":
            player.dir = "right"

        num_buttons = joystick.get_numbuttons()
        if hat_x == 0 and hat_y == 0:
            pass

        try:
            if joystick.get_numaxes() >= 2:
                stick_x = joystick.get_axis(0)
                stick_y = joystick.get_axis(1)
                THRESHOLD = 0.5

                if stick_y < -THRESHOLD and player.dir != "down":
                    player.dir = "up"
                elif stick_y > THRESHOLD and player.dir != "up":
                    player.dir = "down"
                elif stick_x < -THRESHOLD and player.dir != "right":
                    player.dir = "left"
                elif stick_x > THRESHOLD and player.dir != "left":
                    player.dir = "right"
        except pygame.error:
            pass

    def receive_keypress(self, key):
        player1_keys = {"w": "up", "a": "left", "s": "down", "d": "right"}
        player2_keys = {
            keyboard.Key.up: "up",
            keyboard.Key.down: "down",
            keyboard.Key.left: "left",
            keyboard.Key.right: "right",
        }

        try:
            char_key = key.char
            if char_key in player1_keys and self.player1.is_manully_controlled():
                if (
                    (char_key == "w" and self.player1.dir != "down")
                    or (char_key == "s" and self.player1.dir != "up")
                    or (char_key == "a" and self.player1.dir != "right")
                    or (char_key == "d" and self.player1.dir != "left")
                ):
                    self.player1.dir = player1_keys[char_key]
        except AttributeError:
            if key in player2_keys and self.player2.is_manully_controlled():
                if (
                    (key == keyboard.Key.up and self.player2.dir != "down")
                    or (key == keyboard.Key.down and self.player2.dir != "up")
                    or (key == keyboard.Key.left and self.player2.dir != "right")
                    or (key == keyboard.Key.right and self.player2.dir != "left")
                ):
                    self.player2.dir = player2_keys[key]

    def check_crash(self, head, player):
        if not (
            head in self.player1.trail
            or head in self.player2.trail
            or head[0] == 0
            or head[0] == self.screen.width - 1
            or head[1] == 0
            or head[1] == self.screen.height - 1
        ):
            return

        text = f"GAME OVER! Player {player} lose!"
        center_x = self.screen.width // 2 - len(text) // 2
        bottom_y = self.screen.height - 1
        for i, char in enumerate(text):
            self.screen.print_on_coordinate(center_x + i, bottom_y, char, "red")

        self.game_over = True
        self.screen.stop_idle()

    def next_move_player1(self):
        x, y = self.player1.next_move(
            self.screen.width, self.screen.height, self.player2.trail, self.player2.head
        )
        self.check_crash((x, y), 1)
        if not self.game_over:
            self.player1.move_to(x, y)
            self.screen.print_on_coordinate(x, y, "▅", self.player1.color)

    def next_move_player2(self):
        x, y = self.player2.next_move(
            self.screen.width, self.screen.height, self.player1.trail, self.player1.head
        )
        self.check_crash((x, y), 2)
        if not self.game_over:
            self.player2.move_to(x, y)
            self.screen.print_on_coordinate(x, y, "▅", self.player2.color)

    def run(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            bg_thread = threading.Thread(target=self.screen.idle, daemon=True)
            bg_thread.start()


            if self.allow_keyboard:
                listener = keyboard.Listener(on_press=self.receive_keypress)
                listener.start()

            while not self.game_over:
                if self.allow_joystick and len(self.joysticks) > 0:
                    self.update_joystick_input(self.joysticks[0], self.player1)
                if self.allow_joystick and len(self.joysticks) > 1:
                    self.update_joystick_input(self.joysticks[1], self.player2)

                self.next_move_player1()
                self.next_move_player2()

                time.sleep(1 / SPEED)

            if self.allow_keyboard:
                listener.stop()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main():
    game = TronGame(GAME_WIDTH, GAME_HEIGHT, allow_keyboard=True, allow_joystick=True)
    game.run()


while True:
    main()
    time.sleep(5)
