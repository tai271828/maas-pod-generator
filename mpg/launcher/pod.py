import gettext
from guacamole import Command

_ = gettext.gettext

class MPGPod(Command):
    def register_arguments(self, parser):
        parser.add_argument(
            'pods', nargs='+',
            help=_("Create pods with the given names"))
        parser.add_argument(
            "-m", "--memory",
            help = _("Memory size of the pods"))
    def invoked(self, ctx):
        print("mpg-cli pod subcommand is called.")
        print("POD is creating {}".format(ctx.args.pods))
