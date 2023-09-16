# worlds-ticket-checker
checks every ~10s if tickets for specified lol worlds 2023 games are available and sends a notification


Requirements:
[Windows-Toasts](https://pypi.org/project/Windows-Toasts/) (Only for Windows notifications in AdvancedChecker)<br>
`$ python -m pip install windows-toasts`

Usage:
- from command line
  - $ python checker.py [options]
- from code
- import Checker or AdvancedChecker from checker.py
- if needed, overload on_available() to implement custom notification
- create an instance with optional parameters
- call checkLoop() to start automatic loop, otherwise call checkAll() to check once
