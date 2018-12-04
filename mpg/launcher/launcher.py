import gettext
from guacamole import Command

_ = gettext.gettext

class Launcher(Command):
    def register_arguments(self, parser):
        parser.add_argument(
            'launcher', nargs='?',
            help=_("Launcher definition file to use"))
    def invoked(self, ctx):
        print("mpg-cli launcher subcommand is called.")
        print("The launcher is creating {}".format(ctx.args.launcher))
