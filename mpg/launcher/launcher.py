import gettext
from guacamole import Command


_ = gettext.gettext


class Launcher(Command):

    name = 'launcher'

    def __init__(self):
        self.launcher = None
        super().__init__()

    def register_arguments(self, parser):
        parser.add_argument(
            'launcher', nargs='?',
            help=_("Launcher definition file to use"))

    def invoked(self, ctx):
        self.launcher = ctx.cmd_toplevel.launcher
        print("The launcher is created by {}".format(ctx.args.launcher))
        print("The config content is \n{}".format(self.launcher.config_yaml))
