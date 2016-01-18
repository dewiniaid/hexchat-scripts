"""
** Creating and Managing Alerts **
/alerts add <alert>
    Creates a new alert named 'name'.
    
    New alerts are initialized using their name as a pattern, equivalent to the following commands:
        /alert pattern <alert> pattern <alert>
        /alert sound <alert> off
        /alert set <alert> word on
    
/alerts del[ete] <alerts...>|ALL
    Deletes alert(s) in the list of names, separated by spaces.  Use "ALL" to delete all alerts.

/alerts copy <alert> <new>
    Duplicates all settings of <alert> to a new alert named <new>.  The new alert's pattern is then set to <new>.

/alerts enable <alerts...>|ALL
/alerts disable <alerts...>|ALL
/alerts on <alerts...>|ALL
/alerts off <alerts...>|ALL
    Enables or disable the selected alert(s).

** Pattern Matching **
/alerts pattern <alert> [<pattern>]
    Sets the pattern for alert, or shows the current pattern if a new pattern is not specified.

    Patterns can contain any text.  Simple wildcards (*) are permitted.  Setting a pattern clears any regex (if one was set).

    Patterns only match on word boundaries by default, but see the 'word' setting.

/alerts regex <alert> [<regex>]
    Sets a regular expression to match for this alert, or shows the current regex if a new regex is not specified.

    Setting a regex clears any pattern (if one was was set).

** Sounds **
/alerts sound <alert> [<soundfile>|OFF]
    Associates <soundfile> with the associated alert, or shows the current sound if a new sound is not specified.  "OFF" disables sound for this alert.

    <soundfile> will be searched for in the following locations (in order):
        Windows: %APPDATA%\HexChat\Sounds, %ProgramFiles%\HexChat\Sounds, %ProgramFiles(x86)%\HexChat\Sounds
        POSIX-like: ~/.config/hexchat/sounds, /sbin/HexChat/share/sounds, /usr/sbin/HexChat/share/sounds, /usr/local/bin/HexChat/share/sounds

    HexChat must be capable of playing the sound using /SPLAY <soundfile>.  On Windows, this means just .wav files, other platform support may vary.

/alerts mute <alerts...>|ALL
/alerts unmute <alerts...>|ALL
    Enables or disables sounds for the selected alerts (without clearing any sound file associations).
    Use this to temporarily silence alerts.

** Colors, Formatting and Other Settings **
/alerts set <alert> <setting> [<value> [<setting> <value> [...]]]
    Changes one or more settings on an alert.  See the Alert Settings sections for a list of what can be set.

    Omitting <value> makes this equivalent to /alerts show

/alerts show <alert> <settings...>|ALL
    Shows the current value of one or more settings on an alert, or all settings if ALL is specified.

/alerts clear <alert> <settings...>|ALL
    Equivalent to /alerts set <alert> off, for each setting specified.  Does not apply to regex or pattern.

/alerts preview <alerts...>|ALL
    Previews one or more alerts.  If a single alert is specified, sound will be played as well.

** Import/Export and Sharing **
/alerts dump <alerts...>|ALL
    Outputs the commands required to re-create the specified alert(s).

/alerts export <alerts...>|ALL
    Outputs text that can be used with /alerts import to create the specified alert(s).

/alerts import <json>
    Imports alert(s)

/alerts share <alerts...>
    Shares alerts with the current channel.  (Alters text in the HexChat input box.)
    NOTE: This sends one message PER ALERT.  Don't spam your channel!  For this reason, there is no /alerts share all

/alerts save
    Saves alerts manually.  (This should happen automatically when exiting HexChat)

** Alert Settings **
The following settings can manipulated using /alerts set, /alerts show and /alerts clear:

:word ON|OFF
    Determines whether the pattern matches on word boundaries only ("ON") or anywhere ("OFF")
    If pattern is "Jon" and input text is "Jonathan", the input will match if word is OFF, but not if word is ON.
    Only used with patterns.  Ignored with a regex.

:bold ON|OFF|LINE
:italic ON|OFF|LINE
:underline ON|OFF|LINE
:reverse ON|OFF|LINE
    Formats output text bold, italic, underline or reverse color.
    When "ON", formats just the text the matched the pattern or regex.
    When "LINE", matches the entire line.
    
    If any of these are set to LINE, any formatting in the original text is stripped.

:color [<foreground>][,<background>]|OFF
    Sets the foreground and background color of text output, or removes this setting if 'OFF' is specified.

    /alerts set alert color 4  - Sets foreground color to 4
    /alerts set alert color ,8  - Sets background color to 8, keeps default foreground color
    /alerts set alert color 4,8  - Sets foreground to 4, background to 8
    /alerts set alert color off - Disables colors

:linecolor [<foreground>][,<background>]|OFF
    As per color, but affects the entire line.  If enabled, any formatting in the original text is stripped.

:enabled ON|OFF
    Determines whether this alert is enabled or not.  See also /alerts enable|on|off|disable

:mute ON|OFF
    Determines whether this alert is muted or not.  See also /alerts mute|unmute

:pattern <pattern>
:regex <regex>
:sound <sound>
    See /alerts pattern, /alerts regex and /alerts sound for instructions.  These settings must be the last setting
    on the line when using /alerts set.
"""
__module_name__ = "alerts"
__module_version__ = "0.4.20160108.002"
__module_description__ = "Custom highlighting and alert messages -- by Dewin"


# Ratsignal.py - https://gist.github.com/anonymous/858898ee52d63cbdb626
# Soundalert.py - https://github.com/hexchat/hexchat-addons/blob/master/python/sound-alert/soundalert.py

import hexchat
import re
import os
import functools
# from threading import Thread
from collections import OrderedDict
import inspect
import json
import itertools
import string

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

def playsound(filename):
    """
    Plays a sound.

    The default implementation uses hexchat's /splay command.

    Bugs: Won't handle filenames with quotes in them, but not much does.  Blame Hexchat.
    """
    hexchat.command("splay \"{}\"".format(filename))

sound_search_path = []
try:
    use_old_sounds = bool(int(hexchat.get_pluginpref("python_alerts_use_old_sounds")))
except Exception:
    use_old_sounds = False

if os.name == "nt":
    sound_search_path = [
        "%APPDATA%\\Hexchat\\Sounds", "%ProgramFiles%/Hexchat/Sounds", "%ProgramFiles(x86)%/Hexchat/Sounds"
    ]
    # Winsound is installed by default on Windows platforms
    if use_old_sounds:
        import winsound
        def playsound(filename):
            winsound.PlaySound(filename, winsound.SND_FILENAME ^ winsound.SND_ASYNC)

elif os.name == "posix":
    sound_search_path = [
        "~/.config/hexchat/sounds", "/sbin/HexChat/share/sounds", "/usr/sbin/HexChat/share/sounds",
        "/usr/local/bin/HexChat/share/sounds",
    ]

    if use_old_sounds:
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

sound_search_path = list(os.path.expandvars(os.path.expanduser(path)) for path in sound_search_path)
# Since we reformat text before sending it, we maintain a blacklist of messages we emit.
# An item is removed from this blacklist is cleared when a matching message is received.


class IRC(object):
    BOLD = '\002'
    ITALIC = '\035'
    UNDERLINE = '\037'
    REVERSE = '\026'
    COLOR = '\003'
    ORIGINAL = '\017'

    MINCOLOR = 0
    MAXCOLOR = 99

    @classmethod
    def color(cls, fg=None, bg=None):
        if isinstance(fg, Iterable) and bg is None:
            return cls.color(*fg)

        if fg is None and bg is None:
            return ""
        fg = "" if fg is None else "{:02d}".format(fg)
        bg = "" if bg is None else "{:02d}".format(bg)
        rv = cls.COLOR + fg
        if bg:
            rv += "," + bg
        return rv


class Color(tuple):
    def str(self, sep=';', condense=True):
        rv = sep.join("" if x is None else str(x) for x in self)
        if condense:
            return rv.rstrip(sep)
        return rv

    def __str__(self):
        return self.str()

    @classmethod
    def fromstring(cls, s, sep=';'):
        color = list(None if not x.strip() else int(x.strip()) for x in s.split(sep, 2))
        return Color(color[:2])


class Alert(object):
    """
    Stores a single alert.
    """
    LINE = object()  # Symbol
    FORMAT_ATTRIBUTES = ('bold', 'italic', 'underline', 'reverse')
    BOOLEAN_ATTRIBUTES = ('word', 'mute', 'enabled')
    COLOR_ATTRIBUTES = ('color', 'linecolor')
    NONECOLORTUPLE = (None, None)

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
        self.linecolor = None

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
        if self.linecolor is not None:
            self.strip |= 1  # Strip colors

        # Line colors
        if self.linecolor is not None:
            lp += IRC.color(self.linecolor)

        # Suffixes
        if lp:
            ls = IRC.ORIGINAL

            # Calculate the optimal suffix based on line- and highlight-formatting
            if not mp and self.color is None:
                ms = ''
            elif self.color is not None and self.color != self.linecolor:
                # Reset to defaults and reset line_prefix
                ms = IRC.ORIGINAL + lp
            else:
                # No colors are involved, just repeat prefix to undo anything it did
                ms = mp
        else:
            # No line-specific formatting, just revert to defaults
            ms = IRC.ORIGINAL

        # Match color
        if self.color is not None and self.color != self.linecolor:
            mp += IRC.color(self.color)

        self.wrap_line = (lp, ls) if lp else None
        self.wrap_match = (mp, ms) if mp else None

    def update(self):
        if self.color == self.NONECOLORTUPLE:
            self.color = None
        if self.linecolor == self.NONECOLORTUPLE:
            self.linecolor = None
        self.update_wrapper()

        # Build a regular expression, or maybe we already have one.
        if self.pattern:
            t = ".*".join(re.escape(chunk) for chunk in self.pattern.split('*'))
            if self.word:
                t = r'\b{}\b'.format(t)
            self.regex = re.compile(t, flags=re.IGNORECASE)

        # Build the substitution string for match wrapping
        if self.wrap_match:
            index = 0  # if self.regex.groups else 0
            self.replacement = lambda x, _w=self.wrap_match, _i=index: _w[0] + x.group(_i) + _w[1]
        else:
            self.replacement = None

    def handle(self, channel, event, words):
        if not self.enabled:
            return False
        if not self.regex.search(words[1]):
            return False

        if self.strip:
            words[1] = hexchat.strip(words[1], -1, self.strip)
        if self.replacement is not None:
            words[1] = self.regex.sub(self.replacement, words[1])
        if self.wrap_line is not None:
            words[1] = self.wrap_line[0] + words[1] + self.wrap_line[1]
            words[0] = self.wrap_line[0] + words[0] + self.wrap_line[1]

        hexchat.unhook(event_hooks[event])
        hexchat.emit_print(event, *words)
        event_hooks[event] = hexchat.hook_print(event, message_hook, event)

        if self.abs_sound is not None and not self.mute:
            playsound(self.abs_sound)

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
        # formats,color,linecolor
        # formats is "bBiIuUrRw" based on what's set.
        f = []
        for attr in itertools.chain(self.FORMAT_ATTRIBUTES, self.BOOLEAN_ATTRIBUTES):  # Uses bBiIuUrR and wem
            value = getattr(self, attr)
            if not value:
                continue
            if value is self.LINE:
                f.append(attr[0].upper())
            else:
                f.append(attr[0].lower())

        for attr in self.COLOR_ATTRIBUTES:
            f.append(",")
            value = getattr(self, attr)
            if value is not None:
                f.append(str(value))
        rv['f'] = "".join(f)

        if self.pattern is not None:
            if self.pattern != self.name:
                rv['p'] = self.pattern
        else:
            rv['r'] = self.regex.pattern

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
            fmt, *colorparts = d['f'].split(",")

            for attr, value in itertools.zip_longest(cls.COLOR_ATTRIBUTES, colorparts, fillvalue=""):
                if not value:
                    setattr(rv, attr, None)
                    continue
                setattr(rv, attr, Color.fromstring(value))

            for attr in cls.FORMAT_ATTRIBUTES:  # Uses bBiIuUrR
                if attr[0].lower() in fmt:
                    setattr(rv, attr, True)
                elif attr[0].upper() in fmt:
                    setattr(rv, attr, cls.LINE)

            for attr in cls.BOOLEAN_ATTRIBUTES:
                setattr(rv, attr, attr[0].lower() in fmt)

        if 's' in d:
            rv.sound = d['s']
        if 'p' in d:
            rv.pattern = d['p']
        elif 'r' in d:
            rv.pattern = None
            rv.regex = re.compile(d['r'], re.IGNORECASE)
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


def command(name, collect=False, help="", requires_alert=False, raw=False):
    """
    Defines a command and its callign convention.

    :param name: Name of the command.
    :param collect: If True, the final argument uses word_eol instead of word
    :param help: Help text shown if command throws InvalidCommandException.
    :param requires_alert: If True, the first argument of the command is an alert rather than the name of an alert.
    :param raw: If True, parameter parsing beyond what requires_alert requires is not performed, words and word_eol are
        passed mostly as-is.
    :return:
    """
    def decorator(fn, *a, **kw):
        if not raw:
            min_args, max_args = get_num_args(fn)

        @functools.wraps(fn)
        def wrapper(words, word_eol):
            try:
                if not raw:
                    if len(words) < min_args:
                        raise InvalidCommandException("Incorrect number of arguments")
                    if max_args is not None:
                        if collect and len(words) >= max_args:
                            words[max_args - 1] = word_eol[max_args - 1]
                            words = words[0:max_args]
                        elif max_args < len(words):
                            raise InvalidCommandException("Incorrect number of arguments")

                if requires_alert:
                    if not len(words):
                        raise InvalidCommandException("Incorrect number of arguments")
                    alert = alerts.get(words[0].lower())
                    if alert is None:
                        print("Alert '{}' not found.".format(words[0]))
                        return False

                    if raw:
                        return fn(alert, words[1:], word_eol[1:])
                    words[0] = alert

                if raw:
                    return fn(words, word_eol)

                return fn(*words)

            except InvalidCommandException as ex:
                if ex.message:
                    print(ex.message)
                print("Usage: /alerts {} {}".format(name, help))
                return False

        COMMANDS[name] = wrapper
        return fn
    return decorator
alert_command = functools.partial(command, requires_alert=True)


def multi_command(fn):
    def wrapper(*names, **kwargs):
        keys = list(name.strip().lower() for name in names)
        is_all = 'all' in keys

        if is_all:
            return fn(alerts, is_all=True, original=names, **kwargs)

        items = OrderedDict()
        for key, name in zip(keys, names):
            if key in items:
                continue
            alert = alerts.get(key)
            if alert is None:
                print("Alert '{}' not found.".format(name))
                continue
            items[key] = alert

        return fn(items, is_all=False, original=names, **kwargs)
    return wrapper


@command("add", help="<alert>: Add an alert named <alert>")
def cmd_add(name):
    key = name.lower()
    if key in alerts:
        print("Alert '{}' already exists.".format(name))
        return False

    alerts[key] = Alert(name)
    print("Alert '{}' added.".format(name))
    return True


@command("delete", help="<alerts...>|ALL: Delete selected alerts (separated by spaces), or delete all alerts.")
@multi_command
def cmd_delete(items, is_all=None, **unused):
    if is_all:
        print("Deleted {} alert(s)".format(len(alerts)))
        alerts.clear()
        return
    if not items:
        raise InvalidCommandException()
    for key, alert in items.items():
        print("Deleted alert '{}'.".format(alert.name))
        del alerts[key]


def parse_bool(
    s,
    _map={'0': False, 'off': False, 'f': False, 'false': False, '1': True, 'on': True, 't': True, 'true': True}
):
    result = _map.get(s.strip().lower())
    if result is None:
        raise ValueError("Invalid format for boolean")
    return result


def parse_format(s):
    if s.strip().lower() == 'line':
        return Alert.LINE
    return parse_bool(s)


def cmd_setshow_format(alert, setting, value=None):
    isset = value is not None
    if isset:
        try:
            value = parse_format(value)
        except ValueError:
            raise InvalidCommandException("Value for {setting} must must be one of (ON|OFF|LINE)".format(setting))
        setattr(alert, setting, value)
        alert.update()

    value = getattr(alert, setting)
    if value is alert.LINE:
        value = 'line'
    else:
        value = 'on' if value else 'off'
    alert.print("{setting} {action} '{value}'".format(setting=setting, value=value, action='set to' if isset else 'is'))
    return True


def cmd_setshow_boolean(alert, setting, value=None):
    isset = value is not None
    if isset:
        try:
            value = parse_bool(value)
        except ValueError:
            raise InvalidCommandException("Value for {setting} must must be one of (ON|OFF)".format(setting))
        setattr(alert, setting, value)
        alert.update()

    value = 'on' if getattr(alert, setting) else 'off'
    alert.print("{setting} {action} '{value}'".format(setting=setting, value=value, action='set to' if isset else 'is'))
    return True


def cmd_setshow_color(alert, setting, value=None):
    isset = value is not None
    if isset:
        if value.strip().lower() in ('off', 'f', 'false', 'none'):
            value = None
        else:
            try:
                value = Color.fromstring(value, ',')
            except ValueError:
                print("<value> must be one or two comma-separated integers between {} and {} or OFF.".format(IRC.MINCOLOR, IRC.MAXCOLOR))
                return False
            for c in value:
                if c is None:
                    continue
                if not (IRC.MINCOLOR <= c <= IRC.MAXCOLOR):
                    print("<value> must be one or two comma-separated integers between {} and {} or OFF.".format(IRC.MINCOLOR, IRC.MAXCOLOR))
                    return False
        setattr(alert, setting, value)

    value = getattr(alert, setting)
    if value is None:
        value = 'not set'
    else:
        value = value.str(",")
    alert.print("{setting} {action} '{value}'".format(setting=setting, value=value, action='set to' if isset else 'is'))
    return True


@alert_command("pattern", collect=True)
def cmd_setshow_pattern(alert, value=None):
    isset = value is not None
    if isset:
        alert.pattern = value
        alert.update()
    if alert.pattern is None:
        print("Alert {} does not use a pattern.")
    else:
        alert.print(
            "Pattern {action} '{value}' (word matching is {word})"
            .format(value=value, action='set to' if isset else 'is', word='on' if alert.word else 'OFF')
        )
    return True


@alert_command("regex", collect=True)
def cmd_setshow_regex(alert, value=None):
    isset = value is not None
    if isset:
        try:
            regex = re.compile(value, re.IGNORECASE)
        except re.error as ex:
            print("Regular expression error: {}".format(str(ex)))
            return False
        alert.pattern = None
        alert.regex = regex
        print(alert.regex.pattern)
        alert.update()
        print(alert.regex.pattern)

    if alert.pattern is None:
        alert.print(
            "Regex {action} '{value}'"
            .format(value=regex.pattern, action='set to' if isset else 'is')
        )
    else:
        alert.print("Regex is '{}' (derived from pattern: '{}')".format(alert.regex.pattern, alert.pattern))
    return True


@alert_command("sound", collect=True)
def cmd_setshow_sound(alert, value=None):
    isset = value is not None
    if isset:
        if value.strip().lower() in ('off', 'f', 'false', 'none'):
            alert.sound = None
        else:
            alert.sound = value
            if not alert.abs_sound and not value.lower().endswith(".wav"):
                alert.sound = value + ".wav"
                if not alert.abs_sound:
                    alert.sound = value

    if alert.sound:
        if alert.abs_sound:
            msg = "Sound {action} {0.sound} (found at {0.abs_sound})"
        else:
            msg = "Sound {action} {0.sound} " + IRC.BOLD + "(file not found in search path)" + IRC.ORIGINAL
        alert.print(msg.format(alert, action='set to' if isset else 'is'))
    elif isset:
        alert.print("Sound removed.")
    else:
        alert.print("No sound set.")
    return True


@alert_command(
    "set", raw=True,
    help="<alert> (sound|pattern|regex|" + "|".join(itertools.chain(Alert.FORMAT_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES)) + " [<value>]: Change alert settings."
)
def cmd_set(alert, words, word_eol):
    for ix in range(0, len(words), 2):
        setting = words[ix]
        if ix+1 < len(words):
            value = words[ix+1]
            value_eol = word_eol[ix+1]
        else:
            value, value_eol = None, None
        if setting in alert.FORMAT_ATTRIBUTES:
            cmd_setshow_format(alert, setting, value)
            continue
        if setting in alert.BOOLEAN_ATTRIBUTES:
            cmd_setshow_boolean(alert, setting, value)
            continue
        if setting in alert.COLOR_ATTRIBUTES:
            cmd_setshow_color(alert, setting, value)
            continue
        if setting == 'pattern':
            cmd_setshow_pattern(alert, value_eol)
            break
        if setting == 'regex':
            cmd_setshow_regex(alert, value_eol)
            break
        if setting == 'sound':
            cmd_setshow_sound(alert, value_eol)
            break
        raise InvalidCommandException("Unknown setting '{}'.".format(setting))
    alert.update()


@alert_command("show")
def cmd_show(alert, *show):
    show = list(setting.strip().lower() for setting in show)
    if 'all' in show:
        show = list(
            itertools.chain(
                ["sound", "pattern", "regex"],
                Alert.FORMAT_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES
            )
        )

    for setting in show:
        if setting in alert.FORMAT_ATTRIBUTES:
            cmd_setshow_format(alert, setting)
        elif setting in alert.BOOLEAN_ATTRIBUTES:
            cmd_setshow_boolean(alert, setting)
        elif setting in alert.COLOR_ATTRIBUTES:
            cmd_setshow_color(alert, setting)
        elif setting == 'pattern':
            cmd_setshow_pattern(alert)
        elif setting == 'regex':
            cmd_setshow_regex(alert)
        elif setting == 'sound':
            cmd_setshow_sound(alert)
        else:
            print("Unknown setting '{}'.".format(setting))


@multi_command
def cmd_multi_bool(items, is_all=None, attr='enabled', changeto=True, state='enabled', **unused):
    ustate = state.capitalize()

    if not items:
        if is_all:
            print("No alerts are currently defined.")
            return
        raise InvalidCommandException()

    changed = 0
    for alert in items.values():
        value = getattr(alert, attr)
        if value == changeto:
            if not is_all:
                alert.print("Already {}.".format(state))
        else:
            changed += 1
            if not is_all:
                alert.print("{}.".format(ustate))
        setattr(alert, attr, changeto)

    if is_all:
        print("{} {} alert(s)".format(ustate, changed))

cmd_enable = functools.partial(cmd_multi_bool, attr='enabled', state='enabled', changeto=True)
cmd_disable = functools.partial(cmd_multi_bool, attr='enabled', state='disabled', changeto=False)
cmd_mute = functools.partial(cmd_multi_bool, attr='mute', state='muted', changeto=True)
cmd_unmute = functools.partial(cmd_multi_bool, attr='mute', state='unmuted', changeto=False)

command('enable', help="<name>|ALL: Enable selected alert(s)")(cmd_enable)
command('disable', help="<name>|ALL: Disable selected alert(s)")(cmd_disable)
COMMANDS['on'] = COMMANDS['enable']
COMMANDS['off'] = COMMANDS['disable']

command('mute', help="<name>|ALL: Mute selected alert(s)")(cmd_mute)
command('unmute', help="<name>|ALL: Unmute selected alert(s)")(cmd_unmute)


@command("preview")
@multi_command
def cmd_preview(items, is_all=None, original=None, **unused):
    sound = (not is_all) and len(original) == 1
    if is_all and not items:
        print("No alerts are currently defined.")
        return False

    for alert in items.values():
        inner = "(Matching portion)"
        if alert.wrap_match:
            inner = alert.wrap_match[0] + inner + alert.wrap_match[1]
        outer = "Preview of alert formatting {}".format(inner)
        if alert.wrap_line:
            outer = alert.wrap_line[0] + outer + alert.wrap_line[1]
        alert.print(outer)

        if sound and alert.abs_sound:
            playsound(alert.abs_sound)


@command("help", help="[<command-or-setting]>: Shows help.")
def cmd_help(search=None):
    if not search:
        print("{name} version {version} - {description}"
            .format(name=__module_name__, version=__module_version__, description=__module_description__)
        )
    else:
        search = search.lower().strip()
        search = ("/alerts " + search, ":" + search)
        found_start = False
        found_end = False

    section = None
    buffer = []

    for line in __doc__.strip().splitlines():
        is_blank = line == "" or line[0] in string.whitespace

        if line.startswith('**'):
            line = IRC.UNDERLINE + IRC.BOLD + line.strip('*' + string.whitespace).upper() + IRC.ORIGINAL
            section = line
            buffer.clear()
            if search:
                continue

        if search:
            if found_start:
                if is_blank:
                    found_end = True
                elif found_end:
                    found_start = False
                    found_end = False
            else:
                if is_blank and buffer:
                    buffer.clear()
                if any(line.startswith(phrase) for phrase in search):
                    found_start = True
                    found_end = False
                    if section is not None:
                        print(section)
                        section = None
                    if buffer:
                        for text in buffer:
                            print(text)
                        buffer.clear()

        if section and not search:
            section = None
        elif line.startswith("/alerts") or line.startswith(':'):
            if line.startswith(':'):
                line = line[1:]
            line = IRC.BOLD + line + IRC.BOLD

        if search and not found_start:
            if not is_blank:
                buffer.append(line)
        else:
            print(line)


@command("dump", help="<name>|ALL: Dump selected alert(s) to output.")
@multi_command
def cmd_dump(items, is_all=None, **kwargs):
    if not items:
        if is_all:
            print("No alerts are currently defined.")
            return False
        raise InvalidCommandException()

    for alert in items.values():
        print("/alerts add {0.name}".format(alert))
        if alert.pattern is not None:
            if alert.pattern != alert.name:
                print("/alerts pattern {0.name} {0.pattern}".format(alert))
        else:
            print("/alerts regex {0.name} {0.regex.pattern}".format(alert))

        settings = []
        for attr in alert.FORMAT_ATTRIBUTES:
            value = getattr(alert, attr)
            if not value:
                continue
            value = "line" if value is alert.LINE else "on"
            settings.extend([attr, value])
        for attr in alert.COLOR_ATTRIBUTES:
            value = getattr(alert, attr)
            if not value:
                continue
            settings.extend([attr, value.str(",")])
        if not alert.enabled:
            settings.append("enabled off")
        if alert.mute:
            settings.append("mute on")
        if alert.pattern is not None and not alert.word:
            settings.append("word off")
        if alert.sound:
            settings.extend(["sound", alert.sound])

        if settings:
            print("/alerts set {0.name} {1}".format(alert, " ".join(settings)))


@command("export", help="<alerts...>|ALL: Export selected alert(s) as JSON.")
@multi_command
def cmd_export(items, is_all=None, **unused):
    if not items:
        if is_all:
            print("No alerts are currently defined.")
            return False
        raise InvalidCommandException()

    result = [alert.export_dict() for alert in items.values()]
    if len(result) == 1:
        result = result[0]
    print(json.dumps(result, separators=(',', ':')))


@command("share", help="<alerts...>: Share selected alert(s) on current IRC channel.")
def cmd_share(*names):
    if not names:
        raise InvalidCommandException()
    result = OrderedDict()
    for name in names:
        key = name.lower()
        if key == 'all':
            print("/alerts share all is not supported, as it may inadvertently flood channels.")
            return False
        elif key not in alerts:
            print("Alert '{}' not found.".format(name))
            return False

        alert = alerts[key]
        result[alert.name] = alert.export_json()

    for name, output in result.items():
        hexchat.command(
            "SAY [HexChat alerts.py plugin]: Add alert '{name}' with /alerts import {output}"
            .format(name=name, output=output)
        )

@command("import", help="<json>: Import JSON data.", collect=True)
def cmd_import(data):
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
