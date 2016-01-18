"""
Usage:

/alerts add <name>
    Creates a new alert named 'name'.
    
    New alerts are initialized with:
        /alert set <name> pattern <name>
        /alert set <name> sound off
        /alert set <name> word on
    
/alerts del[ete] <names...>|ALL
    Deletes alert(s) in the list of names, separated by spaces.
    ALL: Deletes all alerts.
    
/alerts copy <name> <newname>
    Duplicates all settings of an alert to a new alert.
    
/alerts enable <names...>|ALL
/alerts disable <names...>|ALL
/alerts on <names...>|ALL
/alerts off <names...>|ALL
    Enable or disable the selected alert(s).

/alerts mute <names...>|ALL
/alerts unmute <names...>|ALL
    Enables or disables sounds for the selected alerts (without clearing any sound file associations)

/alerts set <name> sound <file>|OFF
    Associates <file> with the associated alert.  "OFF" disables sound for this alert.  "DEFAULT" chooses the default Hexchat alert sound.
    <file> will be searched for in the following locations (in order):
        Windows: %APPDATA%\Hexchat\Sounds, %ProgramFiles%\Hexchat\Sounds, %ProgramFiles(x86)%\Hexchat\Sounds
        POSIX-like: ~/.config/hexchat/sounds, /sbin/HexChat/share/sounds, /usr/sbin/HexChat/share/sounds, /usr/local/bin/HexChat/share/sounds

/alerts set <name> pattern <pattern>
    Sets the pattern for alert.  This can be any text.  Simple wildcards (*) are permitted.
    This clears anything set using set <name> regex
    
/alerts set <name> word ON|OFF
    Determines whether the pattern matches on word boundaries only ("ON") or anywhere ("OFF")
    If pattern is "Jon" and input text is "Jonathan", the input will match if word is OFF, but not if word is ON.
    Only used when using a pattern.
    
/alerts set <name> regex <expression>
    Matches text matching a particular regular expression.
    This clears anything set using set <name> pattern
    
/alerts set <name> bold ON|OFF|LINE
/alerts set <name> italic ON|OFF|LINE
/alerts set <name> underline ON|OFF|LINE
/alerts set <name> reverse ON|OFF|LINE
    Formats output text bold, italic, underline or reverse color.
    When "ON", formats just the text the matched the pattern or parenthesized portion of the regex.
    When "LINE", matches the entire line.
    
    If any of these are set to LINE, any formatting in the original text is stripped.

/alerts set <name> color <colornumber>|OFF
/alerts set <name> linecolor <colornumber>|OFF
    Changes the color of text output, or removes this setting if 'OFF' is specified.

/alerts dump <names...>|ALL
    Outputs the commands required to re-create the specified alert(s).
    Separate multiple alerts with spaces.
    
/alerts export <names...>|ALL
    Outputs text that can be used with /alerts import to create the specified alert(s).

/alerts import <json>
    Imports alert(s)

/alerts save
    Saves alerts manually.  (This should happen when exiting Hexchat)
"""
__module_name__ = "alerts"
__module_version__ = "0.3"
__module_description__ = "Custom highlighting and alert messages -- by Dewin"


# Ratsignal.py - https://gist.github.com/anonymous/858898ee52d63cbdb626
# Soundalert.py - https://github.com/hexchat/hexchat-addons/blob/master/python/sound-alert/soundalert.py

import hexchat
import re
import os
import functools
from threading import Thread
from collections import OrderedDict
import inspect
import json


def playsound(filename):
    """
    Plays a sound using a OS-dependant methodology.

    The default implementation does nothing.
    :param filename: Filename of sound to play.
    :return:
    """
    return
sound_search_path = []

if os.name == "nt":
    # Winsound is installed by default on Windows platforms
    import winsound
    def playsound(filename):
        winsound.PlaySound(filename, winsound.SND_FILENAME ^ winsound.SND_ASYNC)

    sound_search_path = [
        "%APPDATA%\\Hexchat\\Sounds", "%ProgramFiles%/Hexchat/Sounds", "%ProgramFiles(x86)%/Hexchat/Sounds"
    ]
elif os.name == "posix":
    try:
        import pyxine
    except ImportError:
        print("alerts: Pyxine is missing!  Sound alerts will not be available.")
        print("Install xine, then run 'pip install pyxine' to use sounds in this plugin.")
    else:
        def playsound(filename):
            xine = pyxine.Xine()
            stream = xine.stream_new()
            stream.open(filename)
            stream.Play()

        sound_search_path = [
            "~/.config/hexchat/sounds", "/sbin/HexChat/share/sounds", "/usr/sbin/HexChat/share/sounds",
            "/usr/local/bin/HexChat/share/sounds",
        ]

else:
    print("alerts: Unknown platform.  Sound alerts will not be available.")

sound_search_path = list(os.path.expandvars(os.path.expanduser(path)) for path in sound_search_path)

# Since we reformat text before sending it, we maintain a blacklist of messages we emit.
# An item is removed from this blacklist is cleared when a matching message is received.
# temporary_blacklist = []


class IRC(object):
    BOLD = '\002'
    ITALIC = '\035'
    UNDERLINE = '\037'
    REVERSE = '\026'
    COLOR = '\003'
    ORIGINAL = '\017'

    @classmethod
    def color(cls, c):
        return cls.COLOR + "{:02d}".format(c)


class Alert(object):
    """
    Stores a single alert.
    """
    LINE = object()  # Symbol
    FORMAT_ATTRIBUTES = ('bold', 'italic', 'underline', 'reverse')

    def __init__(self, name):
        self.name = name
        self.word = True
        self.pattern = name
        self.regex = None

        self.bold = False
        self.italic = False
        self.underline = False
        self.reverse = False
        self.color = None
        self.line_color = None

        self._sound = None
        self.abs_sound = None
        self.update()

        self.wrap_line = None
        self.wrap_match = None
        self.replacement = None

        self.enabled = True
        self.mute = False

        self.update()

    def update_wrapper(self):
        """
        Recalculates correct values for wrap_line and wrap_match.
        """
        formats = (
            (self.bold, IRC.BOLD),
            (self.italic, IRC.ITALIC),
            (self.underline, IRC.UNDERLINE),
            (self.reverse, IRC.REVERSE)
        )
        # Line prefix, line suffix, match prefix, match suffix
        lp = ''
        ls = ''
        mp = ''
        ms = ''

        for enabled, s in formats:
            if not enabled:
                continue
            if enabled is self.LINE:
                lp += s
            else:
                mp += s

        # prefix and line_prefix are now set appropriately for b/i/u/r
        # Determine what we're stripping from input, if any.
        self.strip = 0
        if lp:
            self.strip |= 2  # Strip formatting
        if self.line_color is not None:
            self.strip |= 1  # Strip colors

        # Line colors
        if self.line_color is not None:
            lp += IRC.color(self.line_color)

        # Suffixes
        if lp:
            ls = IRC.ORIGINAL

            # Calculate the optimal suffix based on line- and highlight-formatting
            if not mp and self.color is None:
                ms = ''
            elif self.color is not None and self.color != self.line_color:
                if self.line_color is None:
                    # No way to know what the original color was, so reset to defaults and reset line_prefix
                    ms = IRC.ORIGINAL + lp
                else:
                    # Don't care what the original color was, change to line color and toggle anything in prefix
                    ms = mp + IRC.color(self.line_color)
            else:
                # No colors are involved, just repeat prefix to undo anything it did
                ms = mp
        else:
            # No line-specific formatting, just revert to defaults
            ms = IRC.ORIGINAL

        # Match color
        if self.color is not None and self.color != self.line_color:
            mp += IRC.color(self.color)

        self.wrap_line = (lp, ls) if lp else None
        self.wrap_match = (mp, ms) if mp else None

    def update(self):
        self.update_wrapper()

        # Build a regular expression, or maybe we already have one.
        if self.pattern:
            t = ".*".join(re.escape(chunk) for chunk in self.pattern.split('*'))
            if self.word:
                t = r'\b{}\b'.format(t)
            self.regex = re.compile(t, flags=re.IGNORECASE)

        # Build the substitution string for match wrapping
        if self.wrap_match:
            index = 1 if self.regex.groups else 0
            self.replacement = lambda x, _w=self.wrap_match, _i=index: _w[0] + x.group(_i) + _w[1]
        else:
            self.replacement = None

    def handle(self, channel, event, words):
        if not self.enabled:
            return False
        if not self.regex.search(words[1]):
            return False

        if self.abs_sound is not None and not self.mute:
            playsound(self.abs_sound)

        if self.strip:
            words[1] = hexchat.strip(words[1], -1, self.strip)
        if self.replacement is not None:
            words[1] = self.regex.sub(self.replacement, words[1])
        if self.wrap_line is not None:
            words[1] = self.wrap_line[0] + words[1] + self.wrap_line[1]
            words[0] = self.wrap_line[0] + words[0] + self.wrap_line[1]

        # temporary_blacklist.append((channel, event, words))
        hexchat.unhook(event_hooks[event])
        hexchat.emit_print(event, *words)
        event_hooks[event] = hexchat.hook_print(event, message_hook, event)
        # print(event, repr(words))
        return True

    @property
    def sound(self):
        return self._sound

    @sound.setter
    def sound(self, value):
        self._sound = value
        self.update_sound()

    def update_sound(self):
        if self._sound is None:
            self.abs_sound = None
            return

        if os.path.isabs(self._sound):
            if os.path.exists(self._sound):
                self.abs_sound = self._sound
            else:
                self.abs_sound = None
            return

        for path in sound_search_path:
            fn = os.path.join(path, self._sound)
            if os.path.exists(fn):
                self.abs_sound = fn

    def print(self, *a, **kw):
        print("Alert '{}':".format(self.name), *a, **kw)

    def export_dict(self):
        # dict: n=name, f=formatting and flags, s=sound (if set), p=pattern (if needed), r=regex (if needed)
        rv = {'n': self.name}

        # Format key:
        # formats,color,line_color
        # formats is "bBiIuUrRw" based on what's set.
        f = []
        for attr in self.FORMAT_ATTRIBUTES:  # Uses bBiIuUrR
            value = getattr(self, attr)
            if not value:
                continue
            if value is self.LINE:
                f.append(attr[0].upper())
            else:
                f.append(attr[0].lower())
        if self.word:
            f.append("w")
        if self.enabled:
            f.append("e")
        if self.mute:
            f.append("m")

        f.append(",")
        if self.color is not None:
            f.append(str(self.color))
        f.append(",")
        if self.line_color is not None:
            f.append(str(self.line_color))
        rv['f'] = "".join(f)

        if self.pattern is not None:
            if self.pattern != self.name:
                rv['p'] = self.pattern
        else:
            rv['r'] = self.regex

        if self.sound:
            rv['s'] = self.sound
        return rv

    def export_json(self):
        d = self.export_dict()
        return json.dumps(d)

    @classmethod
    def import_dict(cls, d):
        rv = Alert(d['n'])
        if 'f' in d:
            fmt, *parts = d['f'].split(",")
            if len(parts) > 0 and len(parts[0]):
                rv.color = int(parts[0])
            if len(parts) > 1 and len(parts[1]):
                rv.line_color = int(parts[1])
            for attr in cls.FORMAT_ATTRIBUTES:  # Uses bBiIuUrR
                if attr[0].lower() in fmt:
                    setattr(rv, attr, True)
                elif attr[0].upper() in fmt:
                    setattr(rv, attr, cls.LINE)
            rv.word = 'w' in fmt
            rv.enabled = 'e' in fmt
            rv.mute = 'm' in fmt
        if 's' in d:
            rv.sound = d['s']
        if 'p' in d:
            rv.pattern = d['p']
        elif 'r' in d:
            rv.regex = d['r']
        rv.update()
        return rv

    @classmethod
    def import_json(cls, s):
        return cls.import_dict(json.loads(s))

def message_hook(words, word_eol, event):
    channel = hexchat.get_info('channel')

    # try:
    #     temporary_blacklist.remove((channel, event, words))
    #     return None
    # except ValueError:
    #     pass

    for alert in alerts.values():
        if alert.handle(channel, event, words):
            return hexchat.EAT_ALL
    return None


class InvalidCommandException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__()

COMMANDS = OrderedDict()


def get_num_args(fn):
    """
    Returns a tuple of the minimum and maximum number of positional arguments to fn.
    """

    if hasattr(inspect, 'signature'):
        min_count = 0
        max_count = 0
        sig = inspect.signature(fn)
        for param in sig.parameters.values():
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                if max_count is not None:
                    max_count += 1
                if param.default is param.empty:
                    min_count += 1
            if param.kind == param.VAR_POSITIONAL:
                max_count = None
        return min_count, max_count

    spec = inspect.getfullargspec(fn)
    max_count = len(spec.args)
    min_count = max_count - len(spec.defaults)
    if spec.varargs is not None:
        max_count = None
        return min_count, max_count


def command(name, collect=False, help="", requires_alert=False):
    def decorator(fn, *a, **kw):
        min_args, max_args = get_num_args(fn)

        @functools.wraps(fn)
        def wrapper(words, word_eol):
            try:
                if len(words) < min_args:
                    raise InvalidCommandException("Incorrect number of arguments")
                if max_args is not None:
                    if collect and len(words) >= max_args:
                        words[max_args - 1] = word_eol[max_args - 1]
                        words = words[0:max_args]
                    elif max_args < len(words):
                        raise InvalidCommandException("Incorrect number of arguments")

                if requires_alert:
                    alert = alerts.get(words[0].lower())
                    if alert is None:
                        print("Alert '{}' not found.".format(words[0]))
                        return False
                    words[0] = alert

                return fn(*words)

            except InvalidCommandException as ex:
                if ex.message:
                    print(ex.message)
                print("Usage: /alerts {} {}".format(name, help))
                return False

        COMMANDS[name] = wrapper
        return wrapper
    return decorator
alert_command = functools.partial(command, requires_alert=True)


@command("add", help="<name>: Add an alert with <name>")
def cmd_add(name):
    key = name.lower()
    if key in alerts:
        print("Alert '{}' already exists.".format(name))
        return False

    alerts[key] = Alert(name)
    print("Alert '{}' added.".format(name))
    return True


@command("delete", help="<name>|ALL: Delete alert with <name>, or delete all alerts.")
def cmd_delete(*names):
    if not names:
        raise InvalidCommandException()
    for name in names:
        key = name.lower()
        if key == 'all':
            print("Deleted {} alert(s)".format(len(alerts)))
            alerts.clear()
            continue

        if key not in alerts:
            print("Alert '{}' not found.".format(name))
            continue

        del alerts[key]
        print("Deleted alert '{}'.".format(name))
        continue


@alert_command("set", requires_alert=True, collect=True, help="<name> (sound|pattern|word|regex|bold|italic|underline|reverse|color|linecolor) [<value>]: Change alert settings.")
def cmd_set(alert, setting, value=None):
    boolean_map = {
        '0': False, 'off': False, 'f': False, 'false': False,
        '1': True, 'on': True, 't': True, 'true': True
    }

    setting = setting.lower()
    if setting in alert.FORMAT_ATTRIBUTES:
        if value is not None:
            value = value.strip().lower()
            if value == 'line':
                value = alert.LINE
            elif value in boolean_map:
                value = boolean_map[value]
            else:
                raise InvalidCommandException("<value> must be one of (ON|OFF|LINE)")
            setattr(alert, setting, value)
            alert.update()

        value = getattr(alert, setting)
        if value is alert.LINE:
            value = 'line'
        else:
            value = 'on' if value else 'off'
        print("Alert {}: {} is '{}'".format(alert.name, setting, value))
        return True

    if setting == 'word':
        if value is not None:
            value = boolean_map.get(value.strip().lower())
            if value is None:
                raise InvalidCommandException("<value> must be one of (ON|OFF)")
            alert.word = value
            alert.update()

        print("Alert {}: word boundary only is '{}'".format(alert.name, alert.word))
        if alert.pattern is None:
            print("(Note: This setting is ignored when using a regex)")
        return True

    if setting == 'color' or setting == 'linecolor':
        attr = setting
        if attr == 'linecolor':
            attr = 'line_color'

        if value is not None:
            if boolean_map.get(value.strip().lower()) is False:
                value = None
            else:
                try:
                    value = int(value)
                except ValueError:
                    print("<value> must be an integer between 0 and 31 or OFF.")
                    return False
                if not (0 <= value <= 31):
                    print("<value> must be an integer between 0 and 31 or OFF.")
                    return False
            setattr(alert, attr, value)
            alert.update()

        value = getattr(alert, attr)
        if value is None:
            value = 'not set'
        print("Alert {}: {} is {}".format(alert.name, setting, value))
        return True

    if setting == 'pattern':
        if value is not None:
            alert.pattern = value
            alert.update()

        if alert.pattern is None:
            print("Alert {} does not use a pattern.")
            return True

        alert.print("Pattern set to '{}' (word matching is {})".format(alert.pattern, 'on' if alert.word else 'OFF'))
        return True

    if setting == 'regex':
        if value is not None:
            try:
                regex = re.compile(value, re.IGNORECASE)
            except re.error as ex:
                print("Regular expression error: {}".format(str(ex)))
                return False
            alert.regex = regex
            alert.pattern = None
            alert.update()

        if alert.pattern is None:
            alert.print("Regex set to '{}'".format(alert.regex.pattern))
        else:
            alert.print("Regex set to '{}' (derived from pattern: '{}')".format(alert.regex.pattern, alert.pattern))
        return True

    if setting == 'sound':
        if value is not None:
            if value.lower() in ('off', 'none'):
                alert.sound = None
            else:
                alert.sound = value
        if alert.sound:
            if alert.abs_sound:
                msg = "Sound set to {0.sound} (found at {0.abs_sound})"
            else:
                msg = "Sound set to {0.sound} " + IRC.BOLD + "(file not found in search path)" + IRC.ORIGINAL
            alert.print(msg.format(alert))
        else:
            alert.print("Sound is unset.")
        return True

    raise InvalidCommandException('Unknown setting.')


def cmd_enable(*names, enable=True):
    if not names:
        raise InvalidCommandException()

    for name in names:
        key = name.lower()
        if key == 'all':
            changed = 0
            for alert in alerts.values():
                if alert.enabled != enable:
                    changed += 1
                alert.enabled = enable
            print("{} {} alert(s)".format("Enabled" if enable else "Disabled", changed))
            continue

        alert = alerts.get(key)
        if alert is None:
            print("Alert '{}' not found.".format(name))
            continue

        if alert.enabled == enable:
            alert.print("Already ", "enabled" if enable else "disabled")
            continue
        alert.enabled = enable
        alert.print("enabled" if enable else "disabled")
        continue
command('enable', False, "<name>|ALL: Enable selected alert(s)")(cmd_enable)
command('disable', False, "<name>|ALL: Disable selected alert(s)")(functools.partial(cmd_enable, enable=False))
COMMANDS['on'] = COMMANDS['enable']
COMMANDS['off'] = COMMANDS['disable']


def cmd_mute(*names, mute=True):
    if not names:
        raise InvalidCommandException()

    for name in names:
        key = name.lower()
        if key == 'all':
            changed = 0
            for alert in alerts.values():
                if alert.mute != mute:
                    changed += 1
                alert.mute = mute
            print("{} {} alert(s)".format("Muted" if mute else "Unmuted", changed))
            continue

        alert = alerts.get(key)
        if alert is None:
            print("Alert '{}' not found.".format(name))
            continue

        if alert.mute == mute:
            alert.print("Already", "muted" if mute else "unmuted")
            continue
        alert.mute = mute
        alert.print("muted" if mute else "unmuted")
        continue
command('mute', False, "<name>|ALL: Mute selected alert(s)")(cmd_mute)
command('unmute', False, "<name>|ALL: Unmute selected alert(s)")(functools.partial(cmd_mute, mute=False))


@command("help")
def cmd_help(*unused):
    print("{name} version {version}".format(name=__module_name__, version=__module_version__))
    print("{description}".format(description=__module_description__))
    for line in __doc__.strip().splitlines():
        if line.startswith("/alerts"):
            line = IRC.BOLD + line + IRC.BOLD
        print(line)


@command("dump", help="<name>|ALL: Dump selected alert(s) to output.")
def cmd_dump(*names):
    if not names:
        raise InvalidCommandException()
    for name in names:
        key = name.lower()
        if key == 'all':
            t = alerts.values()
        elif key not in alerts:
            print("Alert '{}' not found.".format(name))
            continue
        else:
            t = [alerts[key]]

        for alert in t:
            print("/alerts add {0.name}".format(alert))
            if not alert.enabled:
                print("/alerts disable {0.name}".format(alert))

            if alert.pattern is not None:
                if alert.pattern != alert.name:
                    print("/alerts set {0.name} pattern {0.pattern}".format(alert))
                if not alert.word:
                    print("/alerts set {0.name} word off".format(alert))
            else:
                print("/alerts set {0.name} regex {0.regex.pattern}".format(alert))

            if alert.sound:
                print("/alerts set {0.name} sound {0.sound}".format(alert))


            for attr in ("bold", "italic", "underline", "reverse"):
                value = getattr(alert, attr)
                if not value:
                    continue
                value = "line" if value is alert.LINE else "on"
                print("/alerts set {0.name} {attr} {value}".format(alert, attr=attr, value=value))

            if alert.color is not None:
                print("/alerts set {0.name} color {0.color}".format(alert))
            if alert.line_color is not None:
                print("/alerts set {0.name} linecolor {0.line_color}".format(alert))
            if alert.mute:
                print("/alerts mute {0.name}".format(alert))


@command("export", help="<name>|ALL: Export selected alert(s) as JSON.")
def cmd_export(*names):
    if not names:
        raise InvalidCommandException()
    result = []
    for name in names:
        key = name.lower()
        if key == 'all':
            t = alerts.values()
        elif key not in alerts:
            print("Alert '{}' not found.".format(name))
            continue
        else:
            t = [alerts[key]]

        for alert in t:
            result.append(alert.export_dict())

    if len(result) == 1:
        print(json.dumps(result[0], separators=(',', ':')))
        return
    print(json.dumps(result, separators=(',', ':')))

@command("import", help="<json>: Import JSON data.", collect=True)
def cmd_import(data):
    print(repr(data))
    try:
        result = json.loads(data)
    except Exception as ex:
        print("Failed to import:", str(ex))
        return False

    if not isinstance(result, list):
        result = [result]

    ok = True
    new_alerts = OrderedDict()
    for ix, chunk in enumerate(result):
        try:
            alert = Alert.import_dict(chunk)
        except Exception as ex:
            print("Failed to import entry {}:".format(ix), str(ex))
            ok = False
            continue
        key = alert.name.lower()
        if key in alerts:
            print("Failed to import entry {}: Alert '{}' already exists.".format(ix, alert.name))
            ok = False
            continue
        if key in new_alerts:
            print("Failed to import entry {}: Alert '{}' defined previously in import.".format(ix, alert.name))
            ok = False
            continue
        new_alerts[key] = alert

    if ok:
        alerts.update(new_alerts)
        print("Imported {} alert(s)".format(len(new_alerts)))
    else:
        print("Imported aborted, error(s) occurred.")


@command("save", help="Forces alerts to save.")
def cmd_save():
    save()
    print("{} alert(s) saved".format(len(alerts)))


@alert_command("copy", help="<name> <newname>: Duplicates all settings of an alert to a new alert.")
def cmd_copy(alert, new):
    key = new.lower()
    if key in alerts:
        print("Alert '{}' already exists".format(key))

    newalert = Alert.import_dict(alert.export_dict())
    newalert.name = new
    newalert.pattern = new
    newalert.update()
    alerts[key] = newalert
    newalert.print("Copied from {0.name}".format(alert))


def command_hook(words, word_eol, userdata):
    if len(words) < 2:
        print("Type '/alerts help' for full usage instructions.")
        return
    _, cmd, *words = words
    word_eol = word_eol[2:]
    cmd = cmd.lower()

    if cmd not in COMMANDS:
        print("Type '/alerts help' for full usage instructions.")
        return

    fn = COMMANDS[cmd]
    fn(words, word_eol)
    return



def save():
    data = list(alert.export_dict() for alert in alerts.values())
    hexchat.set_pluginpref("python_alerts_saved", json.dumps(data))


def load():
    global alerts
    alerts = OrderedDict()
    data = hexchat.get_pluginpref("python_alerts_saved")
    if data is None:
        return
    try:
        result = json.loads(data)
    except Exception as ex:
        print("Failed to load:", str(ex))
        return False

    if not isinstance(result, list):
        result = [result]

    for ix, chunk in enumerate(result):
        try:
            alert = Alert.import_dict(chunk)
        except Exception as ex:
            print("Failed to load entry {}:".format(ix), str(ex))
            ok = False
            continue
        key = alert.name.lower()
        if key in alerts:
            print("Failed to load entry {}: Alert '{}' duplicated in save data.".format(ix, alert.name))
            ok = False
            continue
        alerts[key] = alert


def unload_hook(userdata):
    save()


# Debug:  :Epic23!IceChat9@mib-BFA70C3F.gv.shawcable.net PRIVMSG #RatChat :Derry[PingMeIfNeeded] i Pmed you :P
# Debug:  :Logan_Aigaion!Mibbit@mib-65D3B4C5.fbx.proxad.net PRIVMSG #RatChat :ACTION yawns
# Debug:  :Edmondson[DeepSpace]!Edmondson@mib-B9C62BA2.ip-37-187-192.eu NOTICE Dewin[4kly|coding] :like this?

# Format: username PRIVMSG/NOTICE CHANNEL :message
print(
    ("{name} version {version} loaded.  Type " + IRC.BOLD + "/alerts help" + IRC.ORIGINAL + " for usage instructions")
    .format(name=__module_name__, version=__module_version__)
)
load()
print("{} alert(s) loaded".format(len(alerts)))
hexchat.hook_unload(unload_hook)
hexchat.hook_command("alerts", command_hook, help="Configures custom alerts")

event_hooks = {}
for event in (
    "Channel Msg Hilight", "Channel Message", "Channel Action",
    "Private Message", "Private Message to Dialog", "Private Action", "Private Action to Dialog"
):
    event_hooks[event] = hexchat.hook_print(event, message_hook, event)
