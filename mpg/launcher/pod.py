from guacamole import Command


class MPGPod(Command):
    def invoked(self, ctx):
        print("mpg pod subcommand is called.")
