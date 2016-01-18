# alerts
Improved alerts for Hexchat

## Requirements
* Hexchat
* Python 3.3 or later (tested with Python 3.4).  May also work with Python 2.x, this is untested.

## Installation Instructions
1. Save 'alerts.py' to your Hexchat addons directory.  On Windows, this is located at `%appdata%\HexChat\addons`.  On Linux and OSX, this is probably `./config/hexchat/addons`
2. Ensure the Python plugin is enabled in Hexchat.
3. Type `/py load alerts.py` in Hexchat, or restart Hexchat and the script should automatically load.
4. Type `/alerts help` to see documentation for creating alerts, or see the top of alerts.py

## Known Issues
* There *may* be a Hexchat crashing bug, if you're still experiencing this in 0.3 discontinue use and let me know.
* If Hexchat tries to play a sound from a highlight/PM at the same time this plugin does, Hexchat's sounds wins. Turn off the highlight sounds in Hexchat if this is the case.
* Sound is untested on anything but Windows. Sounds must be .wav files.

## Planned features/wishlist:
* Option to focus the window an alert occurs in.
* Option to filter alerts by channel/etc.
* Option to copy messages or some subset thereof to the current window.

## Changelog
### 0.4
* Lots of bugfixes and code tidying.
* Probably some new bugs.
* Support for background colors
* Support for sharing alerts in the active IRC channel/conversation with /alerts share
* Can now set multiple options simultaneously with one command.
* Revamped help system -- can /alerts help <command-or-setting> in addition to /alerts help by itself
* Use Hexchat's /SPLAY command to play sounds instead of our own solution.

### 0.3
Fixed issue with colors not being restored correctly.

### 0.2
Removed debug code, restructured some to attempt to stop Hexchat crashes, implemented /alerts copy
