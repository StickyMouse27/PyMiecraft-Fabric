from .command import Command


class Server:
    cmd: Command

    def __init__(self) -> None:
        self.cmd = Command(self)

    def log(self, str: str):
        pass  # TODO
