from guacamole import Command

from mpg.launcher.pod import MPGPod

class MPGApplication(Command):
    def invoked(self, ctx):
        print('application subcommand is called.')


class MPG(Command):
    sub_commands = (
        ('application', MPGApplication),
        ('pod', MPGPod)
    )

def main():
    MPG().main()
