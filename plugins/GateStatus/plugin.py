import json
import re
import subprocess
import time

import supybot.conf as conf
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring
_ = PluginInternationalization('GateStatus')

class GateStatus(callbacks.Plugin):
    """This plugin reports gate statuses.
    """
    def __init__(self, irc):
        self.__parent = super(GateStatus, self)
        self.__parent.__init__(irc)

    def fetch_comments(self, change_id, user, hours):
        # only care about comments in the last 24 hours
        limit = time.time() - (60*60*24)

        cmd = ("ssh -p 29418 adarazs@review.openstack.org gerrit query "
            "--format json --comments 10fe7e27a0f44253cdf8e7f6079db684dad47205")
        output = subprocess.check_output(cmd.split(" "), stderr=subprocess.STDOUT)
        output = json.loads(output.split("\n")[0])

        comments = []
        for comment in output['comments']:
            if comment['reviewer']['username'] in \
                ['jenkins', 'rdo-ci', 'rdo-ci-downstream'] and \
                comment['timestamp'] > limit:
                comments.append(comment)
        return comments

    def check_comments(self, comments):
        results = {}
        for comment in comments:
            for line in comment['message'].split('\n'):
                result = re.match(r'^[*-] (?P<job>.*?) (?P<url>.*?) : (?P<result>[^ ]+) '
                                    '?(?P<comment>.*)$', line)
                if result:
                    success = result.group('result') == 'SUCCESS'
                    job = result.group('job')
                    if job in results:
                        results[job].append(success)
                    else:
                        results[job] = [success]
        return results

    def job_report(self):
        comments = self.fetch_comments("10fe7e27a0f44253cdf8e7f6079db684dad47205",
                                "adarazs", 24)
        results = self.check_comments(comments)
        #import pprint
        #pprint.pprint(results)

        failing_jobs = []

        for job in results.keys():
            if len(results[job]) > 1 and results[job][-2:] == [False, False]:
                failing_jobs.append(job)

        if len(failing_jobs) > 0:
            return "FAILING GATE JOBS: %s | check logs @ " \
                   "https://review.openstack.org/430277 and fix them ASAP." % \
                   ', '.join(failing_jobs)
        else:
            return "Gate jobs are working fine."

    @internationalizeDocstring
    def gatestatus(self, irc, msg, args):
        """(no arguments)

        Returns the status of the quickstart-extras gate jobs.
        """
        irc.reply(self.job_report(), prefixNick=False)
    gatestatus = wrap(gatestatus)

Class = GateStatus

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
