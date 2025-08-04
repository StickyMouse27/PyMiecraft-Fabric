from .decorator_base import DecoratorBase


class When(DecoratorBase):
    when: str

    def __init__(self, when: str) -> None:
        self.when = when

    def modify(self) -> None:
        print(f"when: {self.when}")


once = When("once")
