from .decorator_base import DecoratorBase


class At(DecoratorBase):
    at: str

    def __init__(self, at: str) -> None:
        self.at = at

    def modify(self) -> None:
        print(f"at: {self.at}")


atStart: At = At("start")
atTick: At = At("tick")
