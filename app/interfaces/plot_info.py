# abstract class for basic plot information (shared between flora and fauna)

from abc import ABC, abstractmethod

class PlotInformation(ABC):
    @abstractmethod
    def get_temp(self) -> float:
        pass

    @abstractmethod
    def get_all_fauna(self) -> list:
        pass

    @abstractmethod
    def get_all_flora(self) -> list:
        pass
