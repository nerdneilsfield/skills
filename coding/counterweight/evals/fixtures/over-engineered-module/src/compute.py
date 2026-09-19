from abc import ABC, abstractmethod


class ValueProvider(ABC):
    @abstractmethod
    def get(self, n: int) -> int:
        raise NotImplementedError


class DefaultProvider(ValueProvider):
    def get(self, n: int) -> int:
        return n


class ProviderFactory:
    def __init__(self, provider: ValueProvider | None = None) -> None:
        self.provider = provider or DefaultProvider()

    def make(self) -> ValueProvider:
        return self.provider


class ComputeService:
    def __init__(self, factory: ProviderFactory | None = None) -> None:
        self.factory = factory or ProviderFactory()

    def compute(self, n: int) -> int:
        return self.factory.make().get(n) * 2


def compute(n: int) -> int:
    return ComputeService().compute(n)
