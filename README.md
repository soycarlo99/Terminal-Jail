# Terminal Jail ⌨️🔒

A CLI typing trainer that locks your terminal until you achieve your typing goals! Practice typing with Wikipedia articles, custom texts, or classic pangrams while tracking your speed and accuracy.

## Features

- **Terminal Lock** 🔒 - Locks your terminal until you reach your WPM and accuracy goals
- **Custom Texts** 📚 - Import practice text from PDF, EPUB, or TXT files
- **Live Stats** 📊 - Real-time WPM tracking and accuracy feedback with color-coded errors
- **Smart Fallback** 🌐 - Automatically fetches Wikipedia articles, falls back to pangrams if needed
- **Progress Tracking** 📈 - Visual cursor and progress indicators
- **Daily Practice** ⏰ - Optional shell integration for daily typing exercises

## Install

```bash
git clone https://github.com/YOUR-USERNAME/terminal-typing-jail.git
cd terminal-typing-jail
pip install -r requirements.txt
```

## Usage

### Basic Run

```bash
./terminal_jail.py
```

### Set WPM Goal

```bash
./terminal_jail.py --set-wpm 60
```

### Use Custom Text

```bash
./terminal_jail.py --import-text novel.pdf
```

## Controls

| Key | Action |
|-----|--------|
| ESC | Emergency exit |
| ← Backspace | Delete character |

## Success Criteria

- Meet or exceed your WPM goal (default: 40 WPM)
- Maintain 95% or higher accuracy
- Terminal remains locked until both criteria are met

## Daily Practice Setup

Add to your `.bashrc` or `.zshrc` for automated daily practice:

```bash
if [ -t 0 ]; then
    [ ! -f ~/.typing_jail_last ] && echo "0" > ~/.typing_jail_last
    LAST_RUN=$(date -r ~/.typing_jail_last +%s 2>/dev/null || echo 0)
    NOW=$(date +%s)
    if [ $((NOW - LAST_RUN)) -ge 86400 ]; then
        ~/path/to/terminal_jail.py && {
            date +%s > ~/.typing_jail_last
            clear
        }
    fi
fi
```

This setup:
- Checks if 24 hours have passed since last successful practice
- Only runs in interactive terminal sessions
- Updates completion timestamp after meeting goals
- Clears screen after successful completion

## Requirements

- python 3.x
- curses (included in Python standard library)
- wikipedia
- PyPDF2
- epub2txt

## License

MIT

---

**Note:** Replace "YOUR-USERNAME" in the clone URL with your actual GitHub username.
