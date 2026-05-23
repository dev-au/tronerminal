import os
import sys
import threading


class Screen:
    def __init__(self, width: int, height: int):
        self.clear_terminal()
        self.width = width
        self.height = height
        self.board_state = [
            [(" ", "black") for _ in range(width)] for _ in range(height)
        ]

        self.stop_idle_event = threading.Event()

    def colored_print(self, text: str, color: str, end: str = "\n"):
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m",
        }
        print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}", end=end)

    def show_error(self, message: str):
        self.colored_print(message, "red")

    def show_info(self, message: str):
        self.colored_print(message, "green")

    def clear_terminal(self):
        os.system("clear")

    def full_screen_check(self):
        size = os.get_terminal_size()
        if size.columns < self.width or size.lines < self.height:
            self.clear_terminal()
            self.show_error(
                f"\n\nTerminal size is too small. Required: {self.width}x{self.height}, Current: {size.columns}x{size.lines}"
            )
            return False
        return True

    def print_on_coordinate(self, x: int, y: int, text: str, color: str = "white", end: str = ""):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        term_x = x + 1
        term_y = y + 1
        print(f"\033[{term_y};{term_x}H", end=end)
        self.colored_print(text, color, end=end)

        self.board_state[y][x] = (text, color)
        sys.stdout.flush()

    def print_on_center(self, text: str, color: str = "white", end: str = ""):
        x = self.width // 2 - len(text) // 2
        y = self.height // 2
        for i in range(len(text)):
            self.print_on_coordinate(x + i, y, text[i], color, end=end)

    def reset_state(self):
        self.clear_terminal()
        for y in range(self.height):
            for x in range(self.width):
                if self.board_state[y][x][0] == " ":
                    continue
                self.print_on_coordinate(
                    x, y, self.board_state[y][x][0], self.board_state[y][x][1]
                )

    def print_on_center(self, text: str, color: str = "white", end: str = ""):
        lines = text.split("\n")
        
        start_y = self.height // 2 - len(lines) // 2
        
        for idx, line in enumerate(lines):
            x = self.width // 2 - len(line) // 2
            y = start_y + idx
            
            for i, char in enumerate(line):
                self.print_on_coordinate(x + i, y, char, color, end=end)

    def ask_question(self, question: str) -> str:
        self.print_on_center(question, "cyan")
        
        lines_count = len(question.split("\n"))
        prompt_y = (self.height // 2) + (lines_count // 2) + 1
        prompt_x = self.width // 2 - 10
        
        print(f"\033[{prompt_y + 1};{prompt_x + 1}H", end="")
        self.colored_print("> ", "green", end="")
        sys.stdout.flush()
        
        return input()

    def ask_multiple_choice(self, question: str, options: list[str]) -> int:
        menu_lines = [question, ""]
        for idx, option in enumerate(options):
            menu_lines.append(f"{idx + 1}. {option}")
            
        full_menu_string = "\n".join(menu_lines)
        
        self.print_on_center(full_menu_string, "yellow")
        total_lines = len(menu_lines)
        prompt_y = (self.height // 2) + (total_lines // 2) + 1
        prompt_text = "Enter choice number: "
        prompt_x = self.width // 2 - (len(prompt_text) + 4) // 2
        
        while True:
            print(f"\033[{prompt_y + 1};{prompt_x + 1}H\033[K", end="")
            self.colored_print(prompt_text, "cyan", end="")
            sys.stdout.flush()
            
            choice = input()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return int(choice) - 1
            error_msg = "Invalid choice. Try again."
            error_x = self.width // 2 - len(error_msg) // 2
            self.print_on_coordinate(error_x, prompt_y + 2, error_msg, "red")

    def idle(self):
        screen_edited = False
        while not self.stop_idle_event.is_set():
            if not self.full_screen_check():
                screen_edited = True
            elif screen_edited:
                self.reset_state()
                screen_edited = False
            self.stop_idle_event.wait(0.1)

    def stop_idle(self):
        self.stop_idle_event.set()
