import sys
from guacamole import Command
from guacamole.core import Ingredient
from guacamole.ingredients import argparse
from guacamole.ingredients import cmdtree
from guacamole.recipes.cmd import CommandRecipe
from mpg.launcher.launcher import Launcher
from mpg.launcher.pod import MPGPod


class LauncherIngredient(Ingredient):
    """Ingredient that adds MPG Launcher support to guacamole."""
    def late_init(self, context):
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

    def main(self, argv=None, exit=True):
        return MPGCommandRecipe(self).main(argv, exit)


def main():
    known_cmds = [x[0] for x in MPGCommand.sub_commands]
    known_cmds += ['-h', '--help']
    if not (set(known_cmds) & set(sys.argv[1:])):
        sys.argv.insert(1, 'launcher')
    MPGCommand().main()
