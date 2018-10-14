from guacamole import Command

from checkbox_ng.config import CheckBoxConfig

from plainbox.impl.secure.config import ValidationError
from plainbox.i18n import gettext as _


class CheckConfig(Command):
    def invoked(self, ctx):
        self.config = CheckBoxConfig.get()
        print(_("Configuration files:"))
        for filename in self.config.Meta.filename_list:
            if filename in self.config.filename_list:
                print(" - {0}".format(filename))
            else:
                print(_(" - {0} (not present)").format(filename))
        print(_("Variables:"))
        for variable in self.config.Meta.variable_list:
            print("   [{0}]".format(variable.section))
            print("   {0}={1}".format(
                variable.name,
                variable.__get__(self.config, self.config.__class__)))
        print(_("Sections:"))
        for section in self.config.Meta.section_list:
            print("   [{0}]".format(section.name))
            section_value = section.__get__(self.config, self.config.__class__)
            if section_value:
                for key, value in sorted(section_value.items()):
                    print("   {0}={1}".format(key, value))
        if self.config.problem_list:
            print(_("Problems:"))
            for problem in self.config.problem_list:
                if isinstance(problem, ValidationError):
                    print(_(" - variable {0}: {1}").format(
                        problem.variable.name, problem.message))
                else:
                    print(" - {0}".format(problem.message))
        else:
            print(_("No validation problems found"))
        return 0 if len(self.config.problem_list) == 0 else 1
