import gettext
from guacamole import Command

_ = gettext.gettext

class Launcher(Command):

    name = 'launcher'

    def register_arguments(self, parser):
        parser.add_argument(
            'launcher', nargs='?',
            help=_("Launcher definition file to use"))
    def invoked(self, ctx):
        self.launcher = ctx.cmd_toplevel.launcher
        print("The launcher is created by {}".format(ctx.args.launcher))
