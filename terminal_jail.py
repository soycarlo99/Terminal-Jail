#!/usr/bin/env python3
import argparse
import curses
import os
import random
import re
import sys
import time

import wikipedia
from epub2txt import epub2txt
from PyPDF2 import PdfReader


class TypingTest:
    def __init__(self, wpm_goal=40, text_source=None):
        self.wpm_goal = wpm_goal
        self.text_source = text_source
        self.text = ""
        self.lines = []
        self.setup_text()
        self.clean_text()

    def clean_text(self):
        # Filter to basic Latin characters and punctuation
        self.text = re.sub(r"[^\x20-\x7E]", "", self.text)
        self.text = " ".join(self.text.split())

        # Ensure minimum length with varied fallbacks
        if len(self.text) < 100:
            self.get_fallback_text()

        # Format into wrapped lines
        self.text = self.text[:300]
        self.lines = [self.text[i : i + 60] for i in range(0, len(self.text), 60)]
        self.text = "\n".join(self.lines)

    def get_fallback_text(self):
        fallbacks = [
            "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. Crazy Frederick bought many very exquisite opal jewels.",
            "How razorback-jumping frogs can level six piqued gymnasts! The five boxing wizards jump quickly. Jackdaws love my big sphinx of quartz.",
            "Bright vixens jump; dozy fowl quack. Quick wafting zephyrs vex bold Jim. Two driven jocks help fax my big quiz. Five quacking zephyrs jolt my wax bed.",
            "Amazingly few discotheques provide jukeboxes. My girl wove six dozen plaid jackets before she quit. Sixty zippers were quickly picked from the woven jute bag.",
        ]
        self.text = random.choice(fallbacks)

    def setup_text(self):
        try:
            if self.text_source:
                if self.text_source.endswith(".pdf"):
                    reader = PdfReader(self.text_source)
                    self.text = " ".join(
                        [page.extract_text() or "" for page in reader.pages]
                    )
                elif self.text_source.endswith(".epub"):
                    self.text = epub2txt(self.text_source)
                else:
                    with open(self.text_source, "r", encoding="utf-8") as f:
                        self.text = f.read()
            else:
                # Get random English Wikipedia content
                page_title = wikipedia.random(pages=1)
                page = wikipedia.page(page_title, auto_suggest=False)
                self.text = page.summary

                # Verify Latin characters
                if not re.match(r"^[\x20-\x7E]+$", self.text):
                    raise ValueError("Non-Latin characters detected")

        except (wikipedia.DisambiguationError, wikipedia.PageError) as e:
            self.get_fallback_text()
        except Exception as e:
            self.get_fallback_text()

    def run_test(self, stdscr):
        curses.curs_set(1)
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if height < 10 or width < 60:
            stdscr.addstr(0, 0, "Terminal too small! Minimum 60x10")
            stdscr.getch()
            return False

        start_row = max(2, (height - len(self.lines) - 6) // 2)
        col_pad = max(0, (width - 60) // 2)

        self.display_centered(
            stdscr, start_row - 2, "Type the following text:", col_pad
        )
        self.display_text(stdscr, start_row, col_pad)

        input_text = []
        index = 0
        start_time = time.time()
        last_blink = start_time
        cursor_visible = True

        while index < len(self.text.replace("\n", "")):
            try:
                now = time.time()
                if now - last_blink > 0.5:
                    cursor_visible = not cursor_visible
                    last_blink = now
                    self.display_progress(
                        stdscr,
                        input_text,
                        start_row,
                        col_pad,
                        cursor_visible,
                        start_time,
                    )

                key = stdscr.getkey()
                cursor_visible = True

            except:
                continue

            if key == "\x1b":
                sys.exit(0)

            if key in ("KEY_BACKSPACE", "\b", "\x7f"):
                if index > 0:
                    index -= 1
                    input_text.pop()
            elif len(key) == 1:
                input_text.append(key)
                index += 1

            self.display_progress(
                stdscr, input_text, start_row, col_pad, True, start_time
            )

        elapsed = time.time() - start_time
        wpm = (len(input_text) / 5) / (elapsed / 60) if elapsed > 0 else 0
        accuracy = sum(
            1 for a, b in zip(self.text.replace("\n", ""), input_text) if a == b
        ) / len(input_text)

        self.display_results(stdscr, wpm, accuracy, height, width)
        return wpm >= self.wpm_goal and accuracy >= 0.95

    def display_centered(self, stdscr, row, text, col_pad):
        x = col_pad + (60 - len(text)) // 2
        try:
            stdscr.addstr(row, max(0, x), text)
        except curses.error:
            pass

    def display_text(self, stdscr, start_row, col_pad):
        for i, line in enumerate(self.lines):
            x = col_pad + (60 - len(line)) // 2
            try:
                stdscr.addstr(start_row + i, max(0, x), line)
            except curses.error:
                pass
        stdscr.refresh()

    def display_progress(
        self, stdscr, input_text, start_row, col_pad, show_cursor, start_time
    ):
        flat_text = self.text.replace("\n", "")
        current_line = 0
        cursor_pos = None

        for i in range(len(self.lines)):
            stdscr.move(start_row + i, 0)
            stdscr.clrtoeol()

        for i, (correct, typed) in enumerate(zip(flat_text, input_text)):
            if i >= len(input_text):
                break

            current_line = 0
            line_start = 0
            while current_line < len(self.lines) and i >= line_start + len(
                self.lines[current_line]
            ):
                line_start += len(self.lines[current_line])
                current_line += 1

            y = start_row + current_line
            x = col_pad + (60 - len(self.lines[current_line])) // 2 + (i - line_start)

            color = curses.color_pair(1) if correct == typed else curses.color_pair(2)
            try:
                stdscr.addch(y, x, correct, color)
                if i == len(input_text) - 1:
                    cursor_pos = (y, x + 1)
            except curses.error:
                pass

        remaining_start = len(input_text)
        for i in range(remaining_start, len(flat_text)):
            current_line = 0
            line_start = 0
            while current_line < len(self.lines) and i >= line_start + len(
                self.lines[current_line]
            ):
                line_start += len(self.lines[current_line])
                current_line += 1

            y = start_row + current_line
            x = col_pad + (60 - len(self.lines[current_line])) // 2 + (i - line_start)

            try:
                stdscr.addch(y, x, flat_text[i])
            except curses.error:
                pass

        if cursor_pos and show_cursor:
            try:
                stdscr.move(cursor_pos[0], cursor_pos[1])
            except curses.error:
                pass

        elapsed = time.time() - start_time
        wpm = (len(input_text) / 5) / (elapsed / 60) if elapsed > 0 else 0
        stats = f"WPM: {wpm:.1f} (Goal: {self.wpm_goal}) | Accuracy: {len(input_text)/len(flat_text)*100:.1f}%"
        self.display_centered(stdscr, start_row + len(self.lines) + 2, stats, col_pad)
        stdscr.refresh()

    def display_results(self, stdscr, wpm, accuracy, height, width):
        stdscr.clear()
        y = height // 2 - 3
        x = max(0, (width - 50) // 2)
        try:
            stdscr.addstr(y, x, "Test Complete!\n", curses.A_BOLD)
            stdscr.addstr(y + 1, x, f"WPM: {wpm:.1f}\n")
            stdscr.addstr(y + 2, x, f"Accuracy: {accuracy*100:.1f}%\n")
            stdscr.addstr(y + 3, x, f"Goal: {self.wpm_goal} WPM\n")

            result_text = (
                "Success! Press any key to exit..."
                if wpm >= self.wpm_goal and accuracy >= 0.95
                else "Failed! Press any key to try again..."
            )
            color = curses.A_BOLD if "Success" in result_text else curses.color_pair(2)
            stdscr.addstr(y + 5, x, result_text, color)
        except curses.error:
            pass
        stdscr.getch()


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    parser = argparse.ArgumentParser(description="Terminal Typing Jail")
    parser.add_argument("--set-wpm", type=int, help="Set WPM goal")
    parser.add_argument(
        "--import-text", type=str, help="Path to text file, PDF, or EPUB"
    )
    args = parser.parse_args()

    if args.set_wpm:
        with open(os.path.expanduser("~/.typing_jail"), "w") as f:
            f.write(str(args.set_wpm))
        return

    try:
        with open(os.path.expanduser("~/.typing_jail"), "r") as f:
            wpm_goal = int(f.read())
    except:
        wpm_goal = 40

    while True:
        test = TypingTest(wpm_goal, args.import_text)
        if test.run_test(stdscr):
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
