gate-status
===========

Periodically recheck gate jobs and warn about gate errors using an IRC bot.

This repo contains a [supybot/limnoria](https://github.com/ProgVal/Limnoria)
plug-in and a shell script.

The shell script periodically rechecks a dummy Gerrit change to re-run the gate
jobs on it either by commenting "recheck" or rebasing it. This shows the status
of the gate jobs without any breaking change.

The script should be run from crontab, for example:

    0 0-23/8 * * * ~/gate-status/gate-recheck.sh

The limnoria plug-in needs to be placed inside the plugins folder of the
bot's configuration directory, then loaded with

    load GateCheck

while chatting with the bot. This adds a new `gatecheck` command, which

* parses the comments of the specified Gerrit change
* selects comments from specific users
* below a specific age (1 day currently) and
* warns about any job where the last two gate jobs failed.

The command can be scheduled using the `Scheduler` plugin.

    load Scheduler
    repeat gate-nag 7200 gatestatus

Check out `help scheduler repeat` for more info.

Both the script and a plug-in are half baked and full of wired in variables,
published here for the interest of others, but not production ready in any
sense.

The code depends on 'jq' which can be installed on Fedora with

    dnf install jq

Possible improvements are:

* all hard wired values supplied by variables (gerrit server, username, etc.)
* plug-in configration handled by the config engine of limnoria
