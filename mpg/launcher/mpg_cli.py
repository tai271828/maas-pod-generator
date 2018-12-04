import sys
from guacamole import Command
from mpg.launcher.launcher import Launcher
from mpg.launcher.pod import MPGPod

class MPGApplication(Command):
    def invoked(self, ctx):
        print('application subcommand is called.')


class MPGCommand(Command):
    sub_commands = (
        ('launcher', Launcher),
        ('application', MPGApplication),
        ('pod', MPGPod)
    )

def main():
    known_cmds = [x[0] for x in MPGCommand.sub_commands]
    known_cmds += ['-h', '--help']
    if not (set(known_cmds) & set(sys.argv[1:])):
        sys.argv.insert(1, 'launcher')
    MPGCommand().main()
