from guacamole import Command


class MPGApplication(Command):
    def invoked(self, ctx):
        print('application subcommand is called.')


class MPGPod(Command):
    def invoked(self, ctx):
        print("pod subcommand is called.")


class MPG(Command):
    sub_commands = (
        ('application', MPGApplication),
        ('pod', MPGPod)
    )

def main():
    MPG().main()
