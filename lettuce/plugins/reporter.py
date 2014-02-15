import sys
from gettext import gettext as _
from itertools import groupby


class Reporter(object):
    def __init__(self):
        self.failed_scenarios = []
        self.scenarios_and_its_fails = {}

    def wrt(self, what):
        if isinstance(what, unicode):
            what = what.encode('utf-8')
        sys.stdout.write(what)

    def store_failed_step(self, step):
        if step.failed and step.scenario not in self.failed_scenarios:
            self.scenarios_and_its_fails[step.scenario] = step.why
            self.failed_scenarios.append(step.scenario)

    def print_scenario_running(self, scenario):
        pass

    def print_scenario_ran(self, scenario):
        pass

    def print_end(self, total):
        if total.scenarios_passed < total.scenarios_ran:
            self.wrt("\n")
            self.wrt("\n")
            for scenario in self.failed_scenarios:
                reason = self.scenarios_and_its_fails[scenario]
                self.wrt(str(reason.step))
                self.wrt("\n")
                self.wrt(reason.traceback)

        self.wrt("\n")
        word = total.features_ran > 1 and "features" or "feature"
        self.wrt("%d %s (%d passed)\n" % (
            total.features_ran,
            word,
            total.features_passed))

        word = total.scenarios_ran > 1 and "scenarios" or "scenario"
        self.wrt("%d %s (%d passed)\n" % (
            total.scenarios_ran,
            word,
            total.scenarios_passed))

        steps_details = []
        for kind in "failed", "skipped", "undefined":
            attr = 'steps_%s' % kind
            stotal = getattr(total, attr)
            if stotal:
                steps_details.append("%d %s" % (stotal, kind))

        steps_details.append("%d passed" % total.steps_passed)
        word = total.steps_ran > 1 and "steps" or "step"
        self.wrt("%d %s (%s)\n" % (
            total.steps_ran,
            word,
            ", ".join(steps_details)))

        if total.failed_scenarios:
            # print list of failed scenarios, with their file and line number
            print
            print _("List of failed scenarios:")
            print

            for feature, scenarios in groupby(total.failed_scenarios,
                                              lambda s: s.feature):
                print u' * ' + feature.represented(indent=0, annotate=False,
                                                   description=False)

                for scenario in scenarios:
                    print u'    - ' + scenario.represented(
                        indent=0, annotate=False)
                    print u'      (%s:%d)' % (
                        scenario.described_at.file, scenario.described_at.line)

            print
