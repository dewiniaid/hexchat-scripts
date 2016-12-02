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

/alerts move <alert> {FIRST|LAST|BEFORE <target>|AFTER <target>}
    Move an alert to the specified place on the list of alerts.  Only the first matching alert triggers if multiple
    alerts match for an incoming line of text; this can be used to control which alert is first.

/alerts rename <alert> <newname>
    Change the name of an alert.  Note that this does not change what the alert matches.

** Pattern Matching **
/alerts pattern <alert> [<pattern>]
    Sets the pattern for alert, or shows the current pattern if a new pattern is not specified.

    Patterns can contain any text.  Simple wildcards (*) are permitted.  Setting a pattern clears any regex (if one was
    set).

    Patterns only match on word boundaries by default, but see the 'word' setting.

/alerts regex <alert> [<regex>]
    Sets a regular expression to match for this alert, or shows the current regex if a new regex is not specified.

    Setting a regex clears any pattern (if one was was set).

** Sounds **
/alerts sound <alert> [<soundfile>|OFF]
    Associates <soundfile> with the associated alert, or shows the current sound if a new sound is not specified.  "OFF"
    disables sound for this alert.

    <soundfile> will be searched for in the following locations (in order):
        Windows: %APPDATA%\HexChat\Sounds, %ProgramFiles%\HexChat\Sounds, %ProgramFiles(x86)%\HexChat\Sounds
        POSIX-like: ~/.config/hexchat/sounds, /sbin/HexChat/share/sounds, /usr/sbin/HexChat/share/sounds,
        /usr/local/bin/HexChat/share/sounds

    HexChat must be capable of playing the sound using /SPLAY <soundfile>.  On Windows, this means just .wav files,
    other platform support may vary.

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

/alerts colors
    Shows a list of the available colors.

** Filtering **
:filters
    Each alert can have a nickname filter (configured with /alerts nicklist) and a channel filter (NOT YET IMPLEMENTED,
    configured with /alerts chanlist) configured to restrict which users and what channels can trigger the alert.

    The first matching pattern in a filter determines whether the alert is allowed to trigger.  A filter looks like:

    ALLOW pattern,pattern2,pattern3 DENY pattern3 ALLOW pattern4

    If no patterns in a filter trigger, the filter triggers if the last pattern was a DENY rule (thus allowing easy
    expression of "Block these patterns, allow the rest"), and does not trigger if the last pattern was ALLOW (thus
    allowing "Only allow these patterns").

    Patterns support limited wildcards: * matches 0 or more characters, + 1 or more, and ? exactly 1 character.
    Wildcards will never match "!" (separating a nickname from a username) or "@" (separating a username/channel
    from a hostmask/server name).

    Nicknames are matched against patterns by converting them to nick!user@host format, with some simplifications.
    Empty sections are replaced with wildcards, so these all work: "nickname", "user@host", "@host", "!user"

    Channels are matched against patterns by converting them to channel@server format, with simplifications similar
    to the above.  Note that channel names include the "#", and a PM is the 'channel' of the nickname sending the PM.
    Thus, "ALLOW #*" will only allow alerts to trigger in actual channels (not PMs), and "DENY #*" does the opposite.

/alerts nicklist <alert> SET ALLOW|DENY pattern1,pattern2 ALLOW|DENY pattern3...
/alerts nicklist <alert> EDIT|CLEAR
/alerts chanlist <alert> SET ALLOW|DENY pattern1,pattern2 ALLOW|DENY pattern3...
/alerts chanlist <alert> EDIT|CLEAR
    The SET variants replace the current nickname filter or channel filter with the set pattern
    The EDIT variants update Hexchat's input box to contain the current filter so that it can be edited.
    /alerts chanlist is not yet implemented.
    See /alerts help filters

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
    Only used with patterns.  This setting is ignored if you are using regex matching instead of pattern matching.

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

:focus ON|OFF|FORCE
    Whether or not to switch to the window receiving a triggering message.  This only switches what window Hexchat
    has active, it won't cause Hexchat to steal focus from another program.  To avoid inadvertent breaks mid-typing,
    this not trigger if you have text in the input box unless FORCE is specified.

:notify ON|OFF
    If ON, adds a line in your current window if receiving a triggering message in a different window.  Won't trigger
    if focus is ON and it successfully changes windows.

:flash ON|OFF
    Whether or not to flash the titlebar upon receiving a triggering message.

:copy <window>|ON|OFF
    If set, copies triggered alerts to the specified window, which will be created if it doesn't already exist.
    If ON, the window is named ">>Alerts<<".
"""
import re
import os
import functools
from collections import OrderedDict
import inspect
import json
import itertools
import string
import collections.abc

# noinspection PyUnresolvedReferences
import hexchat

__module_name__ = "alerts"
__module_version__ = "0.6.20161130.001"
__module_description__ = "Custom highlighting and alert messages -- by Dewin"


# I used the following scripts as a starting point.  This is way beyond them now, but they're here for reference.
# Ratsignal.py - https://gist.github.com/anonymous/858898ee52d63cbdb626
# Soundalert.py - https://github.com/hexchat/hexchat-addons/blob/master/python/sound-alert/soundalert.py


try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


class Plugin:
    # Try to collect all of our global state under one roof.

    commands = OrderedDict()

    DIRECTION_SYNONYMS = {
        'first': 'first', 'front': 'first', 'begin': 'first', 'beginning': 'first',
        'last': 'last', 'end': 'last', 'back': 'last',
        'before': 'before',
        'after': 'after'
    }

    def _init_sound(self):
        """Initializes sound support"""
        try:
            self.use_old_sounds = bool(int(hexchat.get_pluginpref("python_alerts_use_old_sounds")))
        except Exception:
            self.use_old_sounds = False

        if os.name == "nt":
            paths = [
                "%APPDATA%\\Hexchat\\Sounds", "%ProgramFiles%/Hexchat/Sounds", "%ProgramFiles(x86)%/Hexchat/Sounds"
            ]
        elif os.name == "posix":
            paths = [
                "~/.config/hexchat/sounds", "/sbin/HexChat/share/sounds", "/usr/sbin/HexChat/share/sounds",
                "/usr/local/bin/HexChat/share/sounds",
            ]
        else:
            paths = []
        self.sound_search_path = list(os.path.expandvars(os.path.expanduser(path)) for path in paths)

    def __init__(self):
        self.sound_search_path = None
        self._init_sound()
        self.alerts = AlertDict()
        self.ignore_messages = False  # Prevents us from triggering our own events.

    def playsound(self, filename):
        """
        Plays a sound.

        The default implementation uses hexchat's /splay command.

        Bugs: Won't handle filenames with quotes in them, but not much does.  Blame Hexchat.
        """
        hexchat.command("splay \"{}\"".format(filename))

    def save(self):
        """Save alerts data"""
        data = list(alert.export_dict() for alert in self.alerts.values())
        hexchat.set_pluginpref("python_alerts_saved", json.dumps(data))

    def load(self):
        """Load alerts data"""
        data = hexchat.get_pluginpref("python_alerts_saved")
        if data is None:
            return
        try:
            result = json.loads(data)
        except Exception as ex:
            print("Failed to load alerts:", str(ex))
            return False

        if not isinstance(result, list):
            result = [result]

        self.alerts.clear()

        for ix, data in enumerate(result):
            try:
                alert = Alert.import_dict(data)
            except Exception as ex:
                print("Failed to load entry {}:".format(ix), str(ex))
                ok = False
                continue
            if alert.name in plugin.alerts:
                print("Failed to load entry {}: Alert '{}' duplicated in save data.".format(ix, alert.name))
                ok = False
                continue
            plugin.alerts.append(alert)


class Pattern:
    # Used by regexify to find sequences of normal characters, followed by sequences of wildcard characters
    _wildcard_regexp = re.compile(r'([^*?+]*)([*?+]*)')

    def regexify(self, string, wcpattern="."):
        """
        Takes a wildcarded string and converts it to a regular expression

        :param string: Wildcarded string
        :param wcpattern: When wildcards appear in a string, they match the specified number of occurances of this
            regular expression.  Must be wrapped in parenthesis if appending * or + would not cause the entire pattern
            to repeat.
        :return: Escaped regular expression string
        """
        # Fast return cases
        if not string:
            string = "*"
        if string in ("*", "+"):
            return wcpattern + string
        if string == "?":
            return wcpattern

        # Split string into normal and wildcard portions, build a regex.
        result = []
        for match in self._wildcard_regexp.finditer(string):
            normal, wild = match.groups()
            if normal:
                result.append(re.escape(normal))
            if not wild:
                continue

            result.append(wcpattern)  # Pattern to match.
            # Count how many of each wildcard character occured
            ct = wild.count("+")
            unbounded = ct or ("*" in wild)
            ct += wild.count("?")

            if ct < 2:
                if unbounded:
                    result.append("+" if ct else "*")
                # Other case is "match exactly one", so just continue.
                continue
            wc = "{" + str(ct)
            if unbounded:
                wc += ","
            wc += "}"
            result.append(wc)
        return "".join(result)


class UserPattern(Pattern):
    """
    Represents a pattern that might match a nick!user@host pattern.  Works by compiling patterns into a regex

    Wildcards are permitted in patterns:
        * matches any number of characters
        + matches one or more characters.
        ? matches exactly one character

    For simplicity, pattern formats need not include a full hostmask.  Those that are not will be converted as follows:

    nickname            => nickname!*@*
    user@host           => *!user@host
    nickname!user@host  => as is

    If a pattern would include an empty component, it is replaced by a * wildcard:

    nickname!@host      => nickname!*@host
    !user@host          => *!user@host
    @host               => *!*@host
    """

    # Regex to split nick!user@host and other formats into components.
    _split_regexp = re.compile(
        r"""
        (?x)
        ^(?:
            # Match bare nicknames and empty strings
            (?:(?P<barenick>[^!@]*))
            | # Or match [nick!]user@host or some portion thereof.
            (?:
                (?:(?P<nick>[^!@]*)(?=!))?
                (?:!?(?P<user>[^!@]*)(?=$|@))?
                (?:@?(?P<host>[^!@]*))?
            )
        )$
        """
    )

    def __init__(self, pattern):
        self.text = pattern
        result = self._split_regexp.fullmatch(pattern)
        if not result:
            raise ValueError("Invalid user pattern {!r}".format(pattern))
        result = result.groupdict(None)

        self.nick = result['barenick'] or result['nick'] or '*'
        self.user = result['user'] or '*'
        self.host = result['host'] or '*'

        # Create regex
        regex = r'^{nick}!{user}@{host}$'.format(
            nick=self.regexify(self.nick),
            user=self.regexify(self.user),
            host=self.regexify(self.host)
        )

        # Successively seek out unneccessary wildcards and remove them if they exist as an optimization.
        # This should improve performance since we'll be matching against a lot of incoming text.
        # Some benchmarking also shows that it's faster to use re.search/re.match/re.fullmatch flavors than things like
        # ^.*[...]
        for chunk in ".*$", ".*@", ".*!":
            if not regex.endswith(chunk):
                break
            regex = regex[:-len(chunk)]
        for chunk in "^.*", "!.*", "@.*":
            if not regex.startswith(chunk):
                break
            regex = regex[:len(chunk)]

        # If the entire pattern was empty, regex will be "^".  Special-case this.
        if regex == "^":
            regex = ""
        self.always_matches = (regex == "")

        method = None
        if regex:
            if regex[0] == "^":
                # Pattern anchored at start.  We can ditch the anchor because match() already is anchored.
                if regex[-1] == "$":  # Also anchored at end, use fullmatch
                    method = "fullmatch"
                    regex = regex[1:-1]
                else:
                    method = "match"
                    regex = regex[1:]
            else:
                # Pattern not anchored at start.  Use search
                method = "search"
        self.regex = regex
        self.compiled = re.compile(regex, re.IGNORECASE)
        if method:
            self._match = getattr(self.compiled, method)
        else:  # Match -always- succeeds on an empty regex
            self._match = lambda unused: True
        self.methodname = method or '<True>'

    def match(self, nickuserhost):
        return bool(self._match(nickuserhost))


class IRC:
    BOLD = '\002'
    ITALIC = '\035'
    UNDERLINE = '\037'
    REVERSE = '\026'
    COLOR = '\003'
    ORIGINAL = '\017'

    MINCOLOR = 0
    MAXCOLOR = 99

    @classmethod
    def color(cls, fg=None, bg=None, text=None):
        if isinstance(fg, Iterable) and bg is None:
            return cls.color(*fg)

        if fg is None and bg is None:
            return ""
        fg = "" if fg is None else "{:02d}".format(fg)
        bg = "" if bg is None else "{:02d}".format(bg)
        rv = cls.COLOR + fg
        if bg:
            rv += "," + bg
        if text is None:
            return rv
        return rv + text + rv

    @classmethod
    def bold(cls, text):
        return cls.BOLD + text + cls.BOLD

    @classmethod
    def italic(cls, text):
        return cls.ITALIC + text + cls.ITALIC

    @classmethod
    def underline(cls, text):
        return cls.UNDERLINE + text + cls.UNDERLINE

    @classmethod
    def reverse(cls, text):
        return cls.REVERSE + text + cls.REVERSE


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


class Context:
    """Light wrapper around Hexchat's contexts."""
    #: Attrs that return methods.
    _forward_properties = {'set', 'prnt', 'emit_print', 'command', 'get_info', 'get_list'}
    #: Attrs that return get_list() results.
    _forward_lists = {'channels', 'dcc', 'users', 'ignore', 'notify'}

    def __init__(self, context):
        self.context = context
        self._id = None

    def print(self, *a, **kw):
        return self.context.prnt(*a, **kw)

    def __getattr__(self, item):
        if item in self._forward_properties:
            return getattr(self.context, item)
        if item in self._forward_lists:
            return self.context.get_list(item)
        return self.context.get_info(item)

    @classmethod
    def _make(cls, context):
        if context is None:
            return None
        return cls(context)

    @classmethod
    def focused(cls):
        return cls.find()

    @classmethod
    def current(cls):
        return cls._make(hexchat.get_context())

    # noinspection PyShadowingBuiltins
    @classmethod
    def find(cls, server=None, channel=None, id=None):
        if id is None:
            return cls._make(hexchat.find_context(server, channel))
        channel = channel.lower()
        for ch in hexchat.get_context().get_list('channels'):
            if ch.id == id and ch.channel == channel:
                return cls(ch.context)
        return None

    def __eq__(self, other):
        if other is None:
            return False
        return self.context == other.context

    @property
    def id(self):
        """Returns the server ID of this context.  None if it could not be located."""
        # Unfortunately, Hexchat doesn't provide a sane way to get a context's server ID.
        if self._id is None:
            channels = hexchat.get_list('channels')
            if channels is not None:
                for channel in channels:
                    if channel.context == self.context:
                        self._id = channel.id
                        break
        return self._id


# noinspection PyProtectedMember,PyShadowingBuiltins
class AlertDict(collections.abc.MutableMapping):
    _head = None
    _tail = None
    _dict = {}
    __default = object()

    def __init__(self, it=None):
        if not it:
            return
        # Could make this more efficient for bulk inserts, but meh.
        for alert in it:
            self.append(alert)

    # region Linked-list-like behaviors
    def _link(self, node, *args):
        """Helper function for linked list manipulation."""
        prev = node
        for next in args:
            if prev:
                if next == prev:
                    raise ValueError("A node cannot be located after itself.")
                prev._next = next
            else:
                self._head = next

            if next:
                next._prev = prev
            else:
                self._tail = prev
            prev = next

    def _addormove(self, alert, add=False, prev=None, next=None):
        """Add/move new alerts to an arbitrary location in the list.  Helper function."""
        if add:
            lowername = alert.name.lower()
            if lowername in self:
                if self[lowername] == alert:
                    raise ValueError("Alert {.name!r} is already in this list.".format(alert))
                else:
                    raise ValueError("Name {!r} is in use.".format(alert.name))
            if alert._parent:
                raise ValueError("Alert {.name!r} is already in this list.".format(alert))
        elif alert._parent is not self:
            raise ValueError("Alert {.name!r} is not a member of this list", alert)

        if prev and prev._parent is not self:
            raise ValueError("Previous Alert {!r} is not a member of this list", prev)
        if next and next._parent is not self:
            raise ValueError("Next alert {!r} is not a member of this list", next)

        if next and not prev:
            prev = next._prev
        elif prev and not next:
            next = prev._next

        if add:
            alert._parent = self
            # noinspection PyUnboundLocalVariable
            self._dict[lowername] = alert
        else:
            self._link(alert._prev, alert._next)
        self._link(prev, alert, next)

        return alert

    def append(self, alert):
        """Add new alert to end of list."""
        return self._addormove(alert, True, prev=self._tail)

    def insertbefore(self, alert, before):
        """Add new alert before an existing alert.  If before is None, same as append."""
        if before:
            return self._addormove(alert, True, next=before)
        return self._addormove(alert, True, prev=self._tail)

    def insertafter(self, alert, after):
        """Add new alert after an existing alert.  If after is None, inserts at the beginning of the list."""
        if after:
            return self._addormove(alert, True, prev=after)
        return self._addormove(alert, True, next=self._head)

    def remove(self, alert):
        """Removes an item from this list."""
        if alert._parent is not self:
            raise ValueError("Alert {.name!r} is not a member of this list", alert)

        self._link(alert._prev, alert._next)
        alert._prev = alert._next = alert._parent = None
        del self._dict[alert.name.lower()]
        return alert

    unlink = remove

    def rename(self, alert, name):
        """Renames an item in this list."""
        if alert._parent is not self:
            raise ValueError("Alert {.name!r} is not a member of this list", alert)
        newname = name.lower()
        oldname = alert.name.lower()
        if newname != oldname:
            if newname in self._dict:
                raise ValueError("Name {!r} is already in use.".format(name))
            del self._dict[oldname]
            self._dict[newname] = alert
        alert._name = name

    def movebefore(self, alert, before):
        if before:
            return self._addormove(alert, False, next=before)
        return self._addormove(alert, False, prev=self._tail)

    def moveafter(self, alert, after):
        if after:
            return self._addormove(alert, False, prev=after)
        return self._addormove(alert, False, next=self._head)
    # endregion

    # region Item accessors
    def __getitem__(self, key):
        return self._dict[key.lower()]

    def __setitem__(self, key, value):
        if key in self and self[key] == value:
            return
        lowerkey = key.lower()
        if lowerkey != value.name.lower():
            raise ValueError("Key and alert name mismatch: {!r} != {!r}".format(key, value.name))
        self.append(value)

    def __delitem__(self, key):
        self.remove(self[key.lower()])
    # endregion

    # region Standard mutable mapping methods
    def clear(self):
        for alert in self._dict.values():
            alert._prev = alert._next = alert._parent = None
        self._head = self._tail = None
        self._dict = {}

    def popitem(self):
        if self._tail:
            alert = self.remove(self._tail)
            return alert.name, alert
        raise KeyError
    # endregion

    # region Standard mutable mapping magic methods
    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._dict)
    # endregion

    # region Iteration handling
    class _KeysView(collections.abc.KeysView):
        def __iter__(self):
            yield from self._mapping.iter_keys()

    class _ValuesView(collections.abc.ValuesView):
        def __iter__(self):
            yield from self._mapping.iter_values()

        def __contains__(self, value):
            try:
                return self._mapping[value.name] == value
            except (KeyError, AttributeError):
                return False

    class _ItemsView(collections.ItemsView):
        def __iter__(self):
            yield from self._mapping.iter_items()

        def __contains__(self, item):
            key, value = item
            try:
                if value.name != key:
                    return False
                return self._mapping[key] == value
            except (AttributeError, KeyError):
                return False

    def keys(self):
        return self._KeysView(self)

    def values(self):
        return self._ValuesView(self)

    def items(self):
        return self._ItemsView(self)

    def iter_keys(self):
        yield from (alert.name for alert in self.iter_values())
    __iter__ = iter_keys

    def iter_values(self):
        count = 0
        maxcount = 2*len(self._dict)
        cur = self._head
        while cur:
            count += 1
            if count > maxcount:
                raise RuntimeError(
                    "**Iterated over more items than expected ({} > {}).  Aborting.**".format(count, maxcount)
                )
            yield cur
            cur = cur._next

    def iter_items(self):
        yield from ((alert.name, alert) for alert in self.iter_values())

    pass  # noop to work around Pycharm region bug.
    # endregion


class Alert(object):
    """Stores a single alert."""
    LINE = object()  # Symbol
    FORCE = object()

    # Tristate attributes (boolean + third state)
    # attrname: (third state value, third state value)
    TRISTATE_ATTRIBUTES = OrderedDict((
        ('bold', ('line', LINE)),
        ('italic', ('line', LINE)),
        ('underline', ('line', LINE)),
        ('reverse', ('line', LINE)),
        ('focus', ('force', FORCE)),
    ))
    #
    BOOLEAN_ATTRIBUTES = ('word', 'mute', 'enabled', 'notify', 'flash')
    COLOR_ATTRIBUTES = ('color', 'linecolor')
    NONECOLORTUPLE = (None, None)
    EXPORT_ATTRS = {
        'b': 'bold',
        'e': 'enabled',
        'f': 'flash',
        'g': 'focus',  # g=grab, close enough
        'i': 'italic',
        'm': 'mute',
        'n': 'notify',
        'r': 'reverse',
        'u': 'underline',
        'w': 'word'
    }

    def __init__(self, name):
        self.word = True
        self.regex = None

        self.bold = False
        self.italic = False
        self.underline = False
        self.reverse = False
        self.color = None
        self.linecolor = None

        self._sound = None
        self.abs_sound = None

        self.wrap_line = None
        self.format_line = ""
        self.wrap_match = None
        self.format_match = ""
        self.replacement = None

        self.enabled = True
        self.mute = False

        self.notify = False
        self.focus = False
        self.flash = False
        self.copy = False

        self._name = name
        self.strip = 0
        self.pattern = name
        self._parent = self._prev = self._next = None

        # Nickname and Channel filters:
        # Lists of (bool, filter) tuples, where the bool is True for allow, False for deny.
        self.filters = {'nick': [], 'channel': []}
        self.check_filter = functools.lru_cache(maxsize=128)(self._check_filter)
        self.update()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._parent:
            self._parent.rename(self, value)
        else:
            self._name = value

    def _update_wrappers(self):
        """Recalculates correct values for wrap_line and wrap_match."""
        formats = (
            (self.bold, IRC.BOLD),
            (self.italic, IRC.ITALIC),
            (self.underline, IRC.UNDERLINE),
            (self.reverse, IRC.REVERSE)
        )
        # Line prefix, line suffix, match prefix, match suffix
        lp = ls = mp = ms = ''

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

        if lp:
            self.wrap_line = (lp, ls)
            self.format_line = (lp + "{}" + ls).format
        else:
            self.wrap_line = None
            self.format_line = lambda x: x  # Identity throwaway

        if mp:
            self.wrap_match = (mp, ms)
            self.format_match = (mp + "{}" + ms).format
        else:
            self.wrap_match = self.format_match = None

    def invalidate_filter_cache(self):
        self.check_filter.cache_clear()

    def _check_filter(self, filterkey, string):
        """
        Runs the specified string against the filter identified by filterkey.  Returns TRUE if allowed, FALSE if denied.
        """
        allowed = False  # This causes us to return true if the filterlist is empty.
        for allowed, pattern in self.filters[filterkey]:
            if pattern is None or pattern.always_matches or pattern.match(string):
                return allowed
        return not allowed

    def _dump_filter(self, filterkey):
        return list(
            ("+" if allowed else "-") + (pattern.text if pattern is not None else "")
            for allowed, pattern in self.filters[filterkey]
        ) or None

    def _load_filter(self, filterkey, data, factory):
        if not data or data[0] == "+":
            self.filters[filterkey] = []
            self.invalidate_filter_cache()
            return

        filt = []
        for string in data:
            allow = string[0] == "+"
            text = string[1:]
            if not text:
                filt.append((allow, None))
            else:
                filt.append((allow, factory(text)))

        self.invalidate_filter_cache()
        self.filters[filterkey] = filt

    def describe_filter(self, filterkey):
        buffer = []
        filt = self.filters[filterkey]
        if not filt:
            return None

        previous = None
        for allowed, pattern in filt:
            if pattern is None:
                previous = None
            if allowed is not previous:
                previous = allowed
                buffer.append(" ALLOW " if allowed else " DENY ")
                if pattern is None:
                    continue
            else:
                buffer.append(",")
            buffer.append(pattern.text)
        return "".join(buffer)

    def _precheck_filter(self, filterkey):
        """
        Returns True if the filter would immediately succeed, False if it'd immediately fail, None otherwise.

        Used as a precheck before cacheing.
        """
        if not self.filters[filterkey]:
            return True
        allowed, pattern = self.filters[filterkey][0]
        if pattern is None or pattern.always_matches:
            return allowed
        return None

    def check_nick(self, event):
        # Determines whether the specified nickname would match this event.
        pre = self._precheck_filter('nick')
        if pre is not None:
            return pre
        return self._check_filter('nick', event.fullnick)

    def update(self):
        if self.color == self.NONECOLORTUPLE:
            self.color = None
        if self.linecolor == self.NONECOLORTUPLE:
            self.linecolor = None
        self._update_wrappers()

        # Build a regular expression, or maybe we already have one.
        if self.pattern:
            t = ".*".join(re.escape(chunk) for chunk in self.pattern.split('*'))
            if self.word:
                t = r'\b{}\b'.format(t)
            self.regex = re.compile(t, flags=re.IGNORECASE)

        # Build the substitution string for match wrapping
        if self.format_match:
            index = 0  # if self.regex.groups else 0
            self.replacement = lambda x, _f=self.format_match, _i=index: _f(x.group(_i))
        else:
            self.replacement = None

    def handle(self, event):
        if not self.enabled:  # Skip disabled events
            return False
        if self.pattern is None:  # Strip formatting to test regexes
            message = event.stripped_message
        else:
            message = event.message
        if not self.regex.search(message):  # Skip non-matching events
            return False

        # Nickname and channel filtering
        if not self.check_nick(event):
            return False

        if self.strip and self.pattern is not None:
            message = event.strip_message(self.strip)

        if self.replacement is not None:
            message = self.regex.sub(self.replacement, message)
        nick = self.format_line(event.rawnick)
        message = self.format_line(message)

        hexchat.emit_print(event.event, nick, message, *event.words[2:])

        if self.abs_sound is not None and not self.mute:
            plugin.playsound(self.abs_sound)

        if self.copy:
            copy_to = '>>alerts<<' if self.copy is True else self.copy
            copy_context = Context.find(event.current.network, copy_to, event.current.id)
            if not copy_context:
                event.current.command("QUERY -nofocus " + copy_to)
                copy_context = Context.find(event.current.network, copy_to, event.current.id)
            if not copy_context:
                print(IRC.bold("** Unable to open/create query window **"))
            else:
                if event.is_channel:
                    name = nick + ":" + event.channel
                else:
                    name = nick + ":(PM)"
                copy_context.emit_print("Channel Message", name, message)

        if event.focused != event.current:
            if self.focus and (self.focus is self.FORCE or not event.focused.inputbox):
                event.current.command("GUI FOCUS")
            elif self.notify:
                if event.current.network == event.focused.network:
                    network = ""
                else:
                    network = "/" + event.focused.network
                if event.is_channel:
                    fmt = "[{nick} on {channel}{network}: {message}]"
                else:
                    fmt = "[PM from {nick}{network}: {message}]"
                event.focused.print(
                    fmt.format(
                        nick=event.nick, channel=event.channel, network=network, message=message)
                    )

        if self.flash:
            hexchat.command("GUI FLASH")
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

        for path in plugin.sound_search_path:
            fn = os.path.join(path, self._sound)
            if os.path.exists(fn):
                self.abs_sound = fn

    def print(self, *a, **kw):
        print("Alert '{}':".format(self.name), *a, **kw)

    def export_dict(self):
        # dict: n=name, f=formatting and flags, s=sound (if set), p=pattern (if needed), r=regex (if needed)
        # c=copy (if enabled)
        rv = {'n': self.name}

        # Format key:
        # formats,color,linecolor
        # formats is "bBiIuUrRw" based on what's set.
        f = []
        for letter, attr in self.EXPORT_ATTRS.items():
            value = getattr(self, attr)
            if not value:
                continue
            if attr in self.TRISTATE_ATTRIBUTES and value is self.TRISTATE_ATTRIBUTES[attr][1]:
                f.append(letter.upper())
            else:
                f.append(letter.lower())

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

        if self.copy:
            rv['c'] = 'on' if self.copy is True else self.copy

        rv['N'] = self._dump_filter('nick')
        if not rv['N']:
            del rv['N']

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
            for letter, attr in cls.EXPORT_ATTRS.items():
                if letter.upper() in fmt and attr in cls.TRISTATE_ATTRIBUTES:  # Handles the oddballs.
                    if attr in cls.TRISTATE_ATTRIBUTES:
                        setattr(rv, attr, cls.TRISTATE_ATTRIBUTES[attr][1])
                else:
                    setattr(rv, attr, letter.lower() in fmt)  # Sets initial true/false

        if 's' in d:
            rv.sound = d['s']
        if 'p' in d:
            rv.pattern = d['p']
        elif 'r' in d:
            rv.pattern = None
            rv.regex = re.compile(d['r'], re.IGNORECASE)

        if 'c' in d:
            rv.copy = True if d['c'] == 'on' else d['c']
        else:
            rv.copy = False
        if 'N' in d and d['N'] is not None:
            rv._load_filter('nick', d['N'], UserPattern)
        rv.update()
        return rv

    @classmethod
    def import_json(cls, s):
        return cls.import_dict(json.loads(s))


class LazyProperty(property):
    """
    Creates a lazily-evaluated property.

    Lazy properties work as follows:
    GET:
      - The first 'get' calls the fget function.  If this function does not raise, the value it returns is stored and
        is returned on all subsequent accesses.
      - Subsequent accesses return the cached value
    SET:
      - Calls the property setter as normal.  If autoset is True, a default setter is constructed that updates the
        cached value.
    DEL:
      - Invalidates the cache, such that the next access will use the normal get() function again.

    Cached property values are stored on the object using the same name as the property, except prefixed by an
    an underscore.  Change cache_name to override this.


    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, *, name=None, cache_name=None, autoset=False):
        """
        Constructs a new LazyProperty

        :param fget: Getter implementation.  If None, returns a decorator.
        :param fset: Setter implementation.  If None, the property is read-only (unless autoset is True)
        :param fdel: Deleter implementation.  The default deleter invalidates the property.
        :param doc: Docstring
        :param name: Property name.  Will be the name of one of the getter/setter/deleter functions if available.
        :param cache_name: Cache attribute name.  Defaults to `"_" + name`
        :param autoset: If True, a default setter will be constructed
        """
        if name is None:
            for fn in fget, fset, fdel:
                try:
                    name = fn.__name__
                    break
                except AttributeError:
                    continue
        if cache_name is None:
            if name is None:
                raise ValueError("Must specify `name`, `cache_name`, or function that has a name.")
            cache_name = "_" + name

        self.name = name or fget.__name__
        self.cache_name = cache_name
        self.autoset = autoset
        super().__init__(fget, fset, fdel, doc)

    def _clone(self, **overrides):
        overrides.setdefault('doc', self.__doc__)
        for attr in 'fget', 'fset', 'fdel', 'name', 'cache_name', 'autoset':
            overrides.setdefault(attr, getattr(self, attr))
        return type(self)(**overrides)

    def getter(self, fget):
        return self._clone(fget=fget)

    def setter(self, fset):
        return self._clone(fset=fset)

    def deleter(self, fdel):
        return self._clone(fdel=fdel)

    def __get__(self, instance, owner):
        if not hasattr(instance, self.cache_name):
            setattr(instance, self.cache_name, super().__get__(instance, owner))
        return getattr(instance, self.cache_name)

    def __set__(self, instance, value):
        if self.autoset:
            setattr(instance, self.cache_name, value)
        else:
            return self.__set__(instance, value)

    def __delete__(self, instance):
        if self.fdel:
            return super().__delete__(instance)
        try:
            delattr(instance, self.cache_name)
        except AttributeError:
            pass


class Event:
    """
    Event wrapper

    :ivar words: List of "words" as defined by Hexchat
    :ivar word_eol: As above, but each entry continues to the end of the line
    :ivar event: The event name as passed by HexChat
    :ivar current: The event context.
    :ivar focused: The focused context.
    """
    def __init__(self, words, word_eol, event):
        self.words = words
        self.word_eol = word_eol
        self.event = event
        self.current = Context.current()
        self.focused = Context.focused()


class CommandEvent(Event):
    def __init__(self, words, word_eol, event="command"):
        self.command = words[1].lower()
        self.fn = Plugin.commands.get(self.command)
        super().__init__(words[2:], word_eol[2:], event)

    def call(self):
        self.fn(self)


class ChatEvent(Event):
    """
    Subclass of Event for handling messages from various nicknames.

    :ivar words: List of "words" as defined by Hexchat
    :ivar word_eol: As above, but each entry continues to the end of the line
    :ivar event: The event name as passed by HexChat
    :ivar context: The event context.
    :ivar focused: The focused context.
    """
    def __init__(self, words, word_eol, event):
        self.rawnick = words[0]
        self.message = words[1]
        self.modes = words[2] if len(words) > 2 else None
        self._stripped_message_cache = {}
        self.is_channel = event.lower().startswith("channel")
        super().__init__(words[1:], word_eol[:1], event)

    @LazyProperty
    def hostmask(self):
        if self.is_channel:
            try:
                return next(iter(user for user in self.current.get_list('users') if user.nick == self.nickname))
            except StopIteration:
                raise ValueError("Could not find associated user in user list.")
        else:
            return self.current.get_info('topic')

    @LazyProperty
    def fullnick(self):
        return self.nick + "!" + self.hostmask

    @LazyProperty
    def nick(self):
        return hexchat.strip(self.rawnick)

    @LazyProperty
    def stripped_message(self):
        return self.strip_message()

    @LazyProperty
    def channel(self):
        return self.current.get_info('channel')

    def strip_message(self, flags=3):
        """hexchat.strip(), but caching"""
        if flags not in self._stripped_message_cache:
            self._stripped_message_cache[flags] = hexchat.strip(self.message, -1, flags)
        return self._stripped_message_cache[flags]


def message_hook(words, word_eol, event):
    if len(words) < 2:
        return  # Blank ACTIONs can cause this, just silently discard them.
    if not plugin.ignore_messages:
        try:
            plugin.ignore_messages = True
            event = ChatEvent(words, word_eol, event)

            for alert in plugin.alerts.values():
                if alert.handle(event):
                    return hexchat.EAT_ALL
        finally:
            plugin.ignore_messages = False
    return None


class InvalidCommandException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__()


def command(name, collect=False, help="", requires_alert=False, raw=False):
    """
    Defines a command and its calling convention.

    :param name: Name of the command.
    :param collect: If True, the final argument uses word_eol instead of word
    :param help: Help text shown if command throws InvalidCommandException.
    :param requires_alert: If True, the first argument of the command is an alert rather than the name of an alert.
    :param raw: If True, parameter parsing beyond what requires_alert requires is not performed.  The function receives
        the event and a parsed alert (if any)
    :return:
    """

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

    def decorator(fn, *a, **kw):
        if not raw:
            min_args, max_args = get_num_args(fn)

        @functools.wraps(fn)
        def wrapper(event):
            try:
                ct = len(event.words) + 1  # Fakery, because we'll always add an event argument
                if raw:
                    args = []
                    if requires_alert and event.words:
                        args.append(event.words[0])
                else:
                    args = None
                    if ct < min_args:
                        raise InvalidCommandException("Incorrect number of arguments")
                    if max_args is not None:
                        if collect and ct >= max_args:
                            args = list(event.words[:max_args - 1])
                            args.append(event.word_eol[max_args - 1])
                        elif max_args < ct:
                            raise InvalidCommandException("Incorrect number of arguments")
                    if args is None:
                        args = list(event.words)

                if requires_alert:
                    if not args:
                        raise InvalidCommandException("Incorrect number of arguments")
                    alert = plugin.alerts.get(args[0])
                    if alert is None:
                        print("Alert '{}' not found.".format(args[0]))
                        return False
                    args[0] = alert

                # noinspection PyArgumentList
                return fn(event, *args)
            except InvalidCommandException as ex:
                if ex.message:
                    print(ex.message)
                print("Usage: /alerts {} {}".format(name, help))
                return False

        Plugin.commands[name] = wrapper
        return fn
    return decorator
alert_command = functools.partial(command, requires_alert=True)


def multi_command(fn):
    def wrapper(event, *names, **kwargs):
        keys = list(name.strip().lower() for name in names)
        is_all = 'all' in keys

        if is_all:
            return fn(plugin.alerts, plugin.alerts, is_all=True, original=names, **kwargs)

        items = OrderedDict()
        for key, name in zip(keys, names):
            if key in items:
                continue
            alert = plugin.alerts.get(key)
            if alert is None:
                print("Alert '{}' not found.".format(name))
                continue
            items[key] = alert

        return fn(event, items, is_all=False, original=names, **kwargs)
    return wrapper


@command("add", help="<alert>: Add an alert named <alert>")
def cmd_add(event, name):
    if name in plugin.alerts:
        print("Alert '{}' already exists.".format(name))
        return False

    plugin.alerts.append(Alert(name))
    print("Alert '{}' added.".format(name))
    return True


@command("delete", help="<alerts...>|ALL: Delete selected alerts (separated by spaces), or delete all alerts.")
@multi_command
def cmd_delete(event, items, is_all=None, **unused):
    if is_all:
        print("Deleted {} alert(s)".format(len(plugin.alerts)))
        plugin.alerts.clear()
        return
    if not items:
        raise InvalidCommandException()
    for key, alert in items.items():
        print("Deleted alert '{}'.".format(alert.name))
        del plugin.alerts[key]


@alert_command("rename", help="<alert> <newname>: Rename an alert.  (Does not change what the alert matches.")
def cmd_rename(event, alert, newname):
    if newname == alert:
        print("Well, that was easy.")
        return
    if newname in plugin.alerts:
        print("There's already an alert named '{}'".format(newname))
        return
    oldname = alert.name
    alert.name = newname
    print("Alert '{}' renamed to '{}'".format(oldname, newname))


@alert_command("move", help="<alert> {FIRST|LAST|BEFORE <targetname>|AFTER <targetname>: Rearrange the list of alerts.")
def cmd_move(event, alert, direction, targetname=None):
    direction = direction.lower()
    if direction not in Plugin.DIRECTION_SYNONYMS:
        raise InvalidCommandException("Invalid direction.")
    direction = Plugin.DIRECTION_SYNONYMS[direction]

    if targetname is not None:
        if direction in ('first', 'last'):
            raise InvalidCommandException("This form of /alert move does not use a targetname.")
        target = plugin.alerts.get(targetname)
        if not target:
            print("Target alert '{}' does not exist.".format(targetname))
            return
        if target == alert:
            print("An alert cannot to be {} itself.".format(direction))
            return
    elif direction not in('first', 'last'):
        raise InvalidCommandException("This form of /alert move requires a target.")
    else:
        target = None

    if direction == 'first':
        plugin.alerts.moveafter(alert, None)
        print("Alert '{}' moved to the beginning of the list.".format(alert.name))
        return
    if direction == 'last':
        plugin.alerts.movebefore(alert, None)
        print("Alert '{}' moved to the end of the list.".format(alert.name))
        return
    if direction == 'before':
        plugin.alerts.movebefore(alert, target)
        print("Alert '{}' moved to be before '{}'".format(alert.name, target.name))
        return
    if direction == 'after':
        plugin.alerts.moveafter(alert, target)
        print("Alert '{}' moved to be after'{}'".format(alert.name, target.name))
        return
    raise ValueError("Reached code that should be unreachable.  Please report this as a bug.")


# noinspection PyDefaultArgument
def parse_bool(
    s,
    _map={'0': False, 'off': False, 'f': False, 'false': False, '1': True, 'on': True, 't': True, 'true': True}
):
    result = _map.get(s.strip().lower())
    if result is None:
        raise ValueError("Invalid format for boolean")
    return result


def parse_format(s, alternates=None):
    if alternates:
        s = s.strip().lower()
        if s in alternates:
            return alternates[s]
    return parse_bool(s)


def cmd_setshow_tristate(event, alert, setting, value=None):
    isset = value is not None
    text, obj = alert.TRISTATE_ATTRIBUTES[setting]
    if isset:
        try:
            value = parse_format(value, {text: obj})
        except ValueError:
            raise InvalidCommandException(
                "Value for {setting} must must be one of (ON|OFF|{text})".format(setting=setting, text=text.upper())
            )

        setattr(alert, setting, value)
        alert.update()

    value = getattr(alert, setting)
    if value is obj:
        value = text
    else:
        value = 'on' if value else 'off'
    alert.print("{setting} {action} '{value}'".format(setting=setting, value=value, action='set to' if isset else 'is'))
    return True


def cmd_setshow_boolean(event, alert, setting, value=None):
    isset = value is not None
    if isset:
        try:
            value = parse_bool(value)
        except ValueError:
            raise InvalidCommandException("Value for {} must must be one of (ON|OFF)".format(setting))
        setattr(alert, setting, value)
        alert.update()

    value = 'on' if getattr(alert, setting) else 'off'
    alert.print("{setting} {action} '{value}'".format(setting=setting, value=value, action='set to' if isset else 'is'))
    return True


def cmd_setshow_copy(event, alert, value=None):
    isset = value is not None
    if isset:
        try:
            alert.copy = parse_bool(value)
        except ValueError:
            alert.copy = value
        value = alert.copy
        alert.update()

    if value:
        if value is True:
            value = '>>alerts<<'
        alert.print("copy {action} on (copying to '{copy}')".format(copy=value, action='set to' if isset else 'is'))
    else:
        alert.print("copy {action} off".format(action='set to' if isset else 'is'))


def cmd_setshow_color(event, alert, setting, value=None):
    isset = value is not None
    if isset:
        if value.strip().lower() in ('off', 'f', 'false', 'none'):
            value = None
        else:
            try:
                value = Color.fromstring(value, ',')
            except ValueError:
                print(
                    "<value> must be one or two comma-separated integers between {} and {} or OFF."
                    .format(IRC.MINCOLOR, IRC.MAXCOLOR)
                )
                return False
            for c in value:
                if c is None:
                    continue
                if not (IRC.MINCOLOR <= c <= IRC.MAXCOLOR):
                    print(
                        "<value> must be one or two comma-separated integers between {} and {} or OFF."
                        .format(IRC.MINCOLOR, IRC.MAXCOLOR)
                    )
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
def cmd_setshow_pattern(event, alert, value=None):
    isset = value is not None
    if isset:
        alert.pattern = value
        alert.update()
    if alert.pattern is None:
        print("Alert {} does not use a pattern.")
    else:
        alert.print(
            "Pattern {action} '{value}' (word matching is {word})"
            .format(value=alert.pattern, action='set to' if isset else 'is', word='on' if alert.word else 'OFF')
        )
    return True


@alert_command("regex", collect=True)
def cmd_setshow_regex(event, alert, value=None):
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
            .format(value=alert.regex.pattern, action='set to' if isset else 'is')
        )
    else:
        alert.print("Regex is '{}' (derived from pattern: '{}')".format(alert.regex.pattern, alert.pattern))
    return True


@alert_command("sound", collect=True)
def cmd_setshow_sound(event, alert, value=None):
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
            msg = "Sound {action} {0.sound} " + IRC.bold("(file not found in search path)")
        alert.print(msg.format(alert, action='set to' if isset else 'is'))
    elif isset:
        alert.print("Sound removed.")
    else:
        alert.print("No sound set.")
    return True


@alert_command(
    "set", raw=True,
    help=(
        "<alert> (sound|pattern|regex|copy|" +
        "|".join(itertools.chain(Alert.TRISTATE_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES)) +
        " [<value>]: Change alert settings."
    )
)
def cmd_set(event, alert):
    words = event.words
    for ix in range(1, len(words), 2):
        setting = words[ix]
        if ix+1 < len(words):
            value = words[ix+1]
            value_eol = event.word_eol[ix+1]
        else:
            value, value_eol = None, None
        if setting in alert.TRISTATE_ATTRIBUTES:
            cmd_setshow_tristate(event, alert, setting, value)
            continue
        if setting in alert.BOOLEAN_ATTRIBUTES:
            cmd_setshow_boolean(event, alert, setting, value)
            continue
        if setting in alert.COLOR_ATTRIBUTES:
            cmd_setshow_color(event, alert, setting, value)
            continue
        if setting == 'copy':
            cmd_setshow_copy(event, alert, value)
            continue
        if setting == 'pattern':
            cmd_setshow_pattern(event, alert, value_eol)
            break
        if setting == 'regex':
            cmd_setshow_regex(event, alert, value_eol)
            break
        if setting == 'sound':
            cmd_setshow_sound(event, alert, value_eol)
            break
        raise InvalidCommandException("Unknown setting '{}'.".format(setting))
    alert.update()


@alert_command("show")
def cmd_show(event, alert, *show):
    show = list(setting.strip().lower() for setting in show)
    if 'all' in show or not show:
        show = list(
            itertools.chain(
                ["sound", "pattern", "regex", "focus"],
                Alert.TRISTATE_ATTRIBUTES, Alert.BOOLEAN_ATTRIBUTES
            )
        )

    for setting in show:
        if setting in alert.TRISTATE_ATTRIBUTES:
            cmd_setshow_tristate(event, alert, setting)
        elif setting in alert.BOOLEAN_ATTRIBUTES:
            cmd_setshow_boolean(event, alert, setting)
        elif setting in alert.COLOR_ATTRIBUTES:
            cmd_setshow_color(event, alert, setting)
        elif setting == 'copy':
            cmd_setshow_copy(event, alert)
        elif setting == 'pattern':
            cmd_setshow_pattern(event, alert)
        elif setting == 'regex':
            cmd_setshow_regex(event, alert)
        elif setting == 'sound':
            cmd_setshow_sound(event, alert)
        else:
            print("Unknown setting '{}'.".format(setting))


@multi_command
def cmd_multi_bool(event, items, is_all=None, attr='enabled', changeto=True, state='enabled', **unused):
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
Plugin.commands['on'] = Plugin.commands['enable']
Plugin.commands['off'] = Plugin.commands['disable']

command('mute', help="<name>|ALL: Mute selected alert(s)")(cmd_mute)
command('unmute', help="<name>|ALL: Unmute selected alert(s)")(cmd_unmute)


@command("preview")
@multi_command
def cmd_preview(event, items, is_all=None, original=None, **unused):
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
            plugin.playsound(alert.abs_sound)


@command("version")
def cmd_version(event):
    print("alerts.py version {}".format(__module_version__))


@command("help", help="[<command-or-setting]>: Shows help.")
def cmd_help(event, search=None):
    if not search:
        print(
            "{name} version {version} - {description}"
            .format(name=__module_name__, version=__module_version__, description=__module_description__)
        )
    else:
        search = search.lower().strip()
        search = ("/alerts " + search, ":" + search)

    section = None
    buffer = []

    found_start = False
    found_end = False

    for line in __doc__.strip().splitlines():
        is_blank = line == "" or line[0] in string.whitespace

        if line.startswith('**'):
            line = IRC.underline(IRC.bold(line.strip('*' + string.whitespace).upper()))
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
            line = IRC.bold(line)

        if search and not found_start:
            if not is_blank:
                buffer.append(line)
        else:
            print(line)


@command("dump", help="<name>|ALL: Dump selected alert(s) to output.")
@multi_command
def cmd_dump(event, items, is_all=None, **kwargs):
    if not items:
        if is_all:
            print("No alerts are currently defined.")
            return False
        raise InvalidCommandException()

    for alert in items.values():
        settings = []
        print("/alerts add {0.name}".format(alert))
        if alert.pattern is not None:
            if alert.pattern != alert.name:
                print("/alerts pattern {0.name} {0.pattern}".format(alert))
            if alert.word is not alert.__class__.word:
                settings.extend(("word", 'on' if alert.word else 'off'))
        else:
            print("/alerts regex {0.name} {0.regex.pattern}".format(alert))

        for attr, (text, obj) in alert.TRISTATE_ATTRIBUTES.items():
            value = getattr(alert, attr)
            if value is getattr(alert.__class__, attr):
                continue
            if value is obj:
                value = text
            else:
                value = 'on' if value else 'off'
            settings.extend([attr, value])
        for attr in alert.BOOLEAN_ATTRIBUTES:
            value = getattr(alert, attr)
            if value is getattr(alert.__class__, attr) or (attr == 'word' and alert.pattern is None):
                continue
            settings.extend([attr, 'on' if value else 'off'])
        for attr in alert.COLOR_ATTRIBUTES:
            value = getattr(alert, attr)
            if not value:
                continue
            settings.extend([attr, value.str(",")])
        # if not alert.enabled:
        #     settings.append("enabled off")
        # if alert.mute:
        #     settings.append("mute on")
        # if alert.pattern is not None and not alert.word:
        #     settings.append("word off")
        if alert.sound:
            settings.extend(["sound", alert.sound])
        if alert.copy:
            settings.extend(["copy", 'on' if alert.copy is True else alert.copy])

        if settings:
            print("/alerts set {0.name} {1}".format(alert, " ".join(settings)))


@command("export", help="<alerts...>|ALL: Export selected alert(s) as JSON.")
@multi_command
def cmd_export(event, items, is_all=None, **unused):
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
def cmd_share(event, *names):
    if not names:
        raise InvalidCommandException()
    result = OrderedDict()
    for name in names:
        key = name.lower()
        if key == 'all':
            print("/alerts share all is not supported, as it may inadvertently flood channels.")
            return False
        elif key not in plugin.alerts:
            print("Alert '{}' not found.".format(name))
            return False

        alert = plugin.alerts[key]
        result[alert.name] = alert.export_json()

    for name, output in result.items():
        hexchat.command(
            "SAY [HexChat alerts.py plugin]: Add alert '{name}' with /alerts import {output}"
            .format(name=name, output=output)
        )


@command("import", help="<json>: Import JSON data.", collect=True)
def cmd_import(event, data):
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
        if key in plugin.alerts:
            print("Failed to import entry {}: Alert '{}' already exists.".format(ix, alert.name))
            ok = False
            continue
        if key in new_alerts:
            print("Failed to import entry {}: Alert '{}' defined previously in import.".format(ix, alert.name))
            ok = False
            continue
        new_alerts[key] = alert

    if ok:
        plugin.alerts.update(new_alerts)
        print("Imported {} alert(s)".format(len(new_alerts)))
    else:
        print("Imported aborted, error(s) occurred.")


@command("save", help="Forces alerts to save.")
def cmd_save(event):
    plugin.save()
    print("{} alert(s) saved".format(len(plugin.alerts)))


@alert_command("copy", help="<name> <newname>: Duplicates all settings of an alert to a new alert.")
def cmd_copy(event, alert, new):
    key = new.lower()
    if key in plugin.alerts:
        print("Alert '{}' already exists".format(key))

    newalert = Alert.import_dict(alert.export_dict())
    newalert.name = new
    newalert.pattern = new
    newalert.update()
    plugin.alerts.insertafter(newalert, alert)
    newalert.print("Copied from {0.name}".format(alert))


def cmd_filterlist(event, alert, subcommand, *stanzas, key, filtername, factory):
    subcommand = subcommand.lower()

    if subcommand == 'edit':
        desc = alert.describe_filter(key)
        if not desc:
            print(
                "No {} is configured yet for this alert.  "
                "Add one below, or see /ALERTS HELP FILTERS and /ALERTS HELP {}"
                .format(filtername, event.command)
            )
        command = "/ALERTS {command} {alert} SET{description}".format(
            command=event.command.upper(),
            alert=alert.name,
            description=desc or " ALLOW "
        )
        if desc:
            print("Editing {} for alert '{}'\nCurrent filter is: {}".format(filtername, alert.name, command))
        hexchat.command("SETTEXT " + command)
        return

    if subcommand == 'clear':
        alert.filters[key].clear()
        alert.invalidate_filter_cache()
        print("{} for alert '{}' has been reset to allow all.".format(filtername, alert.name))
        return

    if subcommand != 'set':
        raise InvalidCommandException

    if not stanzas:
        raise InvalidCommandException(
            "No stanzas specified."
            "  To edit the filter list, use '/ALERTS {command} {alert} EDIT'"
            "  To clear the filter list, use '/ALERTS {command} {alert} CLEAR'"
            .format(command=event.command.upper(), alert=alert.name)
        )

    # Pad stanzas to a multiple of 2 for convenience
    filt = []
    for ix in range(0, len(stanzas), 2):
        action = stanzas[ix].lower()
        try:
            texts = stanzas[ix+1]
        except IndexError:  # Exceeded end of list.
            texts = None

        if action in {'allow', 'accept', '+'}:
            allowed = True
        elif action in {'deny', 'reject', 'block', 'ignore', '-'}:
            allowed = False
        else:
            raise InvalidCommandException("Unknown action '{}', expected ALLOW or DENY".format(action))

        if texts is None:
            filt.append((allowed, None))
            continue
        if texts[-1] == ",":
            raise InvalidCommandException(
                "Near '{text}': Pattern list cannot end with a comma.  (HINT: If you were trying to specify multiple"
                " patterns to {action}, they cannot be separated with spaces -- use 'a,b,c' not 'a, b, c')"
                .format(text=texts, action=action)
            )
        texts = texts.split(",")
        for text in texts:
            if not text:
                raise InvalidCommandException("Near '{}': Empty pattern in pattern list.".format(stanzas[ix+1]))
            filt.append((allowed, factory(text)))

    alert.filters[key] = filt
    alert.invalidate_filter_cache()
    print("Updated {} for alert '{}'".format(filtername, alert.name))


alert_command(
    "nicklist",
    help="<alert> EDIT|CLEAR|(SET ALLOW|DENY pattern,pattern... ALLOW|DENY pattern,pattern...):"
         "  Edits the nickname filter."
)(functools.partial(cmd_filterlist, key='nick', filtername='nickname filter', factory=UserPattern))


# noinspection PyProtectedMember
@command("debug")
def cmd_debug(event, name=None):
    # noinspection PyProtectedMember
    def _print_alert():
        print(
            "Key: {key}, Name: {alert.name}, Prev={prev}, Next={next}".format(
                key=key,
                alert=alert,
                prev=alert._prev.name if alert._prev else '<first>',
                next=alert._next.name if alert._next else '<last>'
            )
        )

    print("Alert dictionary view: ")
    for key, alert in plugin.alerts._dict.items():
        _print_alert()

    target_len = len(plugin.alerts._dict)
    cur_len = 0

    print("Alert linkedlist view: ")
    print("Head: {}, Tail: {}".format(
        plugin.alerts._head.name if plugin.alerts._head else '<none>',
        plugin.alerts._tail.name if plugin.alerts._head else '<none>'
    ))
    for key, alert in plugin.alerts.items():
        cur_len += 1
        _print_alert()
        if cur_len > target_len:
            print("** Encountered more items than expected (list may be cyclical), aborting **")
            return


@command("colors", help=": Shows a list of colors")
def cmd_colors(event):
    rowsize = 16
    print("Listing all available colors:")
    for offset in range(IRC.MINCOLOR, IRC.MAXCOLOR+1, rowsize):
        print("  {colors}{reset}".format(
            colors=IRC.bold("".join(
                "{1} {0:02}{2} {0:02} ".format(c, IRC.color(0, c), IRC.color(1, c))
                for c in range(offset, min(offset+rowsize, IRC.MAXCOLOR+1))
            )),
            reset=IRC.ORIGINAL
        ))
    print(
        "HINT: Colors 0-15 correspond to the 'mIRC colors' in your Hexchat preferences.  16-31 correspond to your"
        " 'Local colors'.  Subsequent numbers may map to other interface colors."
    )


def command_hook(words, word_eol, userdata):
    if len(words) < 2:
        print("Type '/alerts help' for full usage instructions.")
        return

    event = CommandEvent(words, word_eol)
    if not event.fn:
        print("Unknown command '{}'".format(event.command))
        print("Type '/alerts help' for full usage instructions.")
    else:
        event.call()
    return hexchat.EAT_ALL


def unload_hook(userdata):
    plugin.save()


plugin = Plugin()
print(
    ("{name} version {version} loaded.  Type " + IRC.bold("/alerts help") + " for usage instructions")
    .format(name=__module_name__, version=__module_version__)
)
plugin.load()
print("{} alert(s) loaded".format(len(plugin.alerts)))
hexchat.hook_unload(unload_hook)
hexchat.hook_command("alerts", command_hook, help="Configures custom alerts")

event_hooks = {}
for event_type in (
    "Channel Msg Hilight", "Channel Message", "Channel Action",
    "Private Message", "Private Message to Dialog", "Private Action", "Private Action to Dialog"
):
    event_hooks[event_type] = hexchat.hook_print(event_type, message_hook, event_type)
