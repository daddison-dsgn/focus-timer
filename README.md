# Focus Timer

Pomodoro-style terminal timer with an ASCII clock and session log. Windows only.

## Usage

```
python timer.py           # 25-min focus + 5-min break (default)
python timer.py 45 10     # custom focus/break in minutes
```

## Controls

| Key | Action |
|-----|--------|
| `S` | Start a focus + break session |
| `L` | View session log |
| `Q` | Quit (or skip current phase) |

Sessions are logged to `sessions.log` in the same directory.
