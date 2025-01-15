

class CommandController:
    def __init__(self):
        self.server = None

    def purge(self):
        self.notify("Server purged!")

    def notify(self, message):
        if self.server is not None and self.server.command is not None:
            self.server.command.notify(message)

    def set_server(self, server):
        self.server = server