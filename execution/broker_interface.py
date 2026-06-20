from abc import ABC
from abc import abstractmethod


class BrokerInterface(ABC):

    @abstractmethod
    def buy(
        self,
        symbol,
        quantity
    ):
        pass

    @abstractmethod
    def sell(
        self,
        symbol,
        quantity
    ):
        pass