from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server


class Command:
    at_a = "@a"
    at_p = "@p"
    at_r = "@r"
    at_s = "@s"
    at_e = "@e"

    def __init__(self, server: "Server") -> None:
        self.server: Server = server

    def cmd(self, cmd: str) -> None:
        self.server.cmd(cmd)

    def __call__(self, cmd: str) -> None:
        self.cmd(cmd)

    def give(self, entity: str, item: str) -> None:
        self.cmd(f"give {entity} {item}")

    # TODO
