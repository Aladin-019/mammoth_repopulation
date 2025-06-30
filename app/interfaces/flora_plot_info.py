# extended plot information interface for flora only

from abc import abstractmethod
from app.interfaces.plot_info import PlotInformation

class FloraPlotInformation(PlotInformation):
    @abstractmethod
    def get_rainfall(self) -> float:
        pass

    @abstractmethod
    def get_snowfall(self) -> float:
        pass

    @abstractmethod
    def get_uv_index(self) -> float:
        pass
