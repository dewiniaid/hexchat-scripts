# alerts
Improved alerts for Hexchat

## Requirements
* [Hexchat](https://hexchat.github.io/) version 2.10 or later
* Hexchat's Python 3 plugin.  (Does not currently work Python 2.x).  Use `/py about` to see if the plugin is installed 
  and the version of Python it expects.  The easiest way to get the plugin on Windows is to rerun the Hexchat installer.
* The correct version of [Python](https://www.python.org/downloads/) for the Python 3 plugin.  (Newer versions will not 
  work.)
  - Hexchat 2.10.2 required Python **3.4.x**
  - Hexchat 2.12.x requires Python **3.5.x**

## Installation Instructions
1. Save `alerts.py` to your Hexchat addons directory.  On Windows, this is located at `%appdata%\HexChat\addons`.  
   On Linux and OSX, this is probably `./config/hexchat/addons`
2. Ensure the correct Python plugin is enabled in Hexchat.  You can check with `/py about`.   
   - If nothing shows up, the easiest way to fix this is to rerun the Hexchat installer and select to install the 
     Python 3 plugin.
3. Type `/py load alerts.py` in Hexchat, or restart Hexchat and the script should automatically load.
4. Type `/alerts help` to see documentation for creating alerts, or read 

## Known Issues
* If Hexchat tries to play a sound from a highlight/PM at the same time this plugin does, Hexchat's sound will win.
  Turn off the highlight sounds in Hexchat if this is an issue.
* Sound is untested on anything but Windows.  Sounds must be playable using Hexchat's `/SPLAY` command.

## Changelog
### 0.6
* Significantly cleaned up and tidied code, and probably introduced several bugs.
* Alerts can now be renamed using `/alerts rename <oldname> <newname>`.  This does not change what text they match on.
* Alerts can now be moved to appear at a different position in the alert list using 
  `/alerts move <alert> {BEFORE <target>|AFTER <target>|FIRST|LAST`.  
  Since only the the first matching alert will trigger, this allows more fine-tuned control over which alert triggers.
* Added the ability to filter alerts by nickname/hostmask (see `/ALERTS NICKLIST`).
  
     
### 0.5.2
* Fix exception spam when receiving an empty message.

### 0.5.1
* Fix issue with notify looking at the wrong variable when comparing networks.

### 0.5-rc1
* Add `/alerts colors` which displays a sample of all of the colors by number.
* Add `/alerts set copy ON|OFF|windowtitle` to copy all triggering messages to a custom query window.
* Add `/alerts focus ON|OFF|FORCE` to focus the window that receives an alert.  If enabled, Hexchat will switch to the
  target window.  This will *NOT* steal focus from outside of Hexchat.  It also will not change windows if you have
  text entered (to avoid accidentally finishing your sentence in the new window) unless you choose *FORCE*
* Add `/alerts notify`, which notifies you in your current window if receiving an alert in a different one.
* Fix several small bugs
* Found lots of new and exciting ways to crash Hexchat and hopefully worked around all of them.

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
