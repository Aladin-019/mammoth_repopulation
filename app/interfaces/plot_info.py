# Abstract class access to basic plot information for both Flora and Faun

from abc import ABC, abstractmethod

class PlotInformation(ABC):
    @abstractmethod
    def get_current_temperature(self, day: int) -> float:
        pass

    @abstractmethod
    def get_all_fauna(self) -> list:
        pass

    @abstractmethod
    def get_all_flora(self) -> list:
        pass

    @abstractmethod
    def get_avg_snow_height(self) -> float:
        pass

    @abstractmethod
    def get_previous_snow_height(self) -> float:
        pass
