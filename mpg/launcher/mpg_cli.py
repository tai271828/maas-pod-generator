import gettext
import sys
import os
import logging

from guacamole import Command
from guacamole.core import Ingredient
from guacamole.ingredients import argparse
from guacamole.ingredients import cmdtree
from guacamole.recipes.cmd import CommandRecipe
from mpg.launcher.launcher import Launcher
from mpg.launcher.pod import MPGPod
from csgen.impl.launcher import LauncherDefinition
from csgen.impl.launcher import DefaultLauncherDefinition


_ = gettext.gettext

_logger = logging.getLogger("mpg-cli")


class LauncherIngredient(Ingredient):

    """Ingredient that adds MPG Launcher support to guacamole."""

    def late_init(self, context):
        if context.args.command1.get_cmd_name() != 'launcher':
            context.cmd_toplevel.launcher = DefaultLauncherDefinition()
            return

        if not context.args.launcher:
            # launcher not supplied from cli - using the default one
            launcher = DefaultLauncherDefinition()
            configs = [
                os.path.expanduser('~/{}'.format(launcher.config_filename)),
                os.path.expanduser('~/.config/{}'.format(
                    launcher.config_filename))]
        else:
            configs = [context.args.launcher]
            try:
                with open(context.args.launcher,
                          'rt', encoding='UTF-8') as stream:
                    first_line = stream.readline()
                    if not first_line.startswith('#!'):
                        stream.seek(0)
                    text = stream.read()
            except IOError as exc:
                _logger.error(_("Unable to load launcher definition: %s"), exc)
                raise SystemExit(1)
            generic_launcher = LauncherDefinition()
            generic_launcher.read_string(text)
            config_filename = os.path.expandvars(
                generic_launcher.config_filename)
            # if wrapper specifies just the basename
            if not os.path.split(config_filename)[0]:
                configs += [
                    os.path.expanduser(
                        '~/{}'.format(config_filename)),
                    os.path.expanduser('~/.config/{}'.format(
                        config_filename))]
            # if wrapper specifies an absolute file
            else:
                configs.append(config_filename)
            launcher = generic_launcher
        launcher.read(configs)

        context.cmd_toplevel.launcher = launcher

        print('LauncherIngredient is called. {}'.format(context))


class MPGCommandRecipe(CommandRecipe):

    """A recipe for using MPG-enhanced commands."""

    def get_ingredients(self):
        return [
            cmdtree.CommandTreeBuilder(self.command),
            cmdtree.CommandTreeDispatcher(),
            argparse.ParserIngredient(),
            LauncherIngredient()
        ]


class MPGCommand(Command):
    """
    A command with MPG-enhanced ingredients.

    If no command is givin, launcher command is assumed.
    See mpg-cli launcher -h for more information.
    """

    sub_commands = (
        ('launcher', Launcher),
        ('pod', MPGPod)
    )

    def main(self, argv=None, cmd_exit=True):
        return MPGCommandRecipe(self).main(argv, cmd_exit)


def main():
    known_cmds = [x[0] for x in MPGCommand.sub_commands]
    known_cmds += ['-h', '--help']
    if not (set(known_cmds) & set(sys.argv[1:])):
        sys.argv.insert(1, 'launcher')
    MPGCommand().main()
