# Terminal Jail ⌨️🔒

A CLI typing trainer that locks your terminal until you achieve your typing goals!

## Features

- **Terminal Lock** 🔒 - Mandatory practice session
- **Custom Texts** 📚 - PDF/EPUB/TXT support
- **Live Stats** 📊 - Real-time WPM & accuracy
- **Smart Fallback** 🌐 - Wikipedia articles + classic pangrams

## Install

```bash
git clone https://github.com/YOUR-USERNAME/terminal-typing-jail.git
cd terminal-jail
pip install -r requirements.txt
```

## Usage

### Basic

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

## Config

Add to .bashrc/.zshrc for daily practice:

```bash
# 1. Terminal Session Check
if [ -t 0 ]; then
# Only proceed if we're in an interactive terminal session (not a script/pipe)
# [ -t 0 ] checks if file descriptor 0 (stdin) is connected to a terminal

    # 2. File Initialization
    [ ! -f ~/.typing_jail_last ] && echo "0" > ~/.typing_jail_last
    # If timestamp file doesn't exist, create it with "0" (Unix epoch timestamp)
    # This ensures first-time users get prompted immediately

    # 3. Timestamp Retrieval
    LAST_RUN=$(date -r ~/.typing_jail_last +%s 2>/dev/null || echo 0)
    # Get last run time from file's modification timestamp:
    # - date -r: shows file's last modification time
    # - +%s: format as Unix timestamp (seconds since 1970-01-01)
    # - 2>/dev/null: suppress error messages
    # - || echo 0: fallback to 0 if file is missing/corrupted

    # 4. Current Time
    NOW=$(date +%s)
    # Get current Unix timestamp

    # 5. Daily Check
    if [ $((NOW - LAST_RUN)) -ge 86400 ]; then
    # Check if 24 hours (86,400 seconds) have passed since last completion
    
        # 6. Run Typing Test
        ~/path/to/terminal_jail.py && {
        # Run the typing test program, and only proceed if successful
            
            # 7. Update Timestamp
            date +%s > ~/.typing_jail_last
            # Write current timestamp to file after successful completion
            
            # 8. Clean Screen
            clear
            # Clear terminal after successful test
        }
    fi
fi
```

## Requirements

- wikipedia
- PyPDF2
- epub2txt

## License

MIT

---

**Note:** Replace "YOUR-USERNAME" in the clone URL with your actual GitHub username.
