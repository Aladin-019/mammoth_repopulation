# Extended plot information interface for Flora and its subclasses only

from abc import abstractmethod
from app.interfaces.plot_info import PlotInformation

class FloraPlotInformation(PlotInformation):
    @abstractmethod
    def get_current_rainfall(self, day: int) -> float:
        pass

    @abstractmethod
    def get_current_snowfall(self, day: int) -> float:
        pass

    @abstractmethod
    def get_current_uv(self, day: int) -> float:
        pass

    @abstractmethod
    def get_current_soil_temp(self, day: int) -> float:
        pass

    @abstractmethod
    def get_current_melt_water_mass(self, day: int) -> float:
        pass

    @abstractmethod
    def get_plot_area(self) -> float:
        pass
