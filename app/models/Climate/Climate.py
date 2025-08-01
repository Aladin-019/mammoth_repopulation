import logging
from typing import Optional
from collections import deque

# Import climate loaders and drivers
from app.data.climate_loaders import TemperatureLoader, SnowfallLoader, RainfallLoader, UVLoader, SoilTemp4Loader, SSRDLoader
from app.models.climate_drivers import TemperatureDriver, SnowfallDriver, RainfallDriver, UVDriver, SoilTemp4Driver, SSRDDriver

from app.interfaces.plot_info import PlotInformation

logger = logging.getLogger(__name__)

# Sensitivity constants for snow depth
SOIL_SENSITIVITY = 5.0         # degrees C per meter of snow change
AIR_SENSITIVITY = 2.0          # degrees C per meter of snow change
MAX_DAILY_SOIL_DELTA = 3.0     # max daily soil temp change
MAX_DAILY_AIR_DELTA = 1.5      # max daily air temp change

# Raw climate data file paths for different biomes
BIOME_FILE_MAP = {
    "southern taiga": {
        "temperature": "app/data/climate_data/daily_temp_stats/krasnoyarsk_daily_temperature_stats.csv",
        "snowfall": "app/data/climate_data/daily_snowfall_stats/krasnoyarsk_daily_snowfall_stats.csv",
        "rainfall": "app/data/climate_data/daily_rainfall_stats/krasnoyarsk_daily_large_scale_rain_stats.csv",
        "uv": "app/data/climate_data/daily_uv_stats/krasnoyarsk_daily_uv_stats.csv",
        "soil_temp4": "app/data/climate_data/daily_soil_temp_stats/level_4_depth/krasnoyarsk_daily_temperature_stats.csv",
        "ssrd": "app/data/climate_data/daily_solar_rad_down_stats/krasnoyarsk_daily_surface_solar_rad_stats.csv"
    },
    "northern taiga": {
        "temperature": "app/data/climate_data/daily_temp_stats/salekhard_daily_temperature_stats.csv",
        "snowfall": "app/data/climate_data/daily_snowfall_stats/salekhard_daily_snowfall_stats.csv",
        "rainfall": "app/data/climate_data/daily_rainfall_stats/salekhard_daily_large_scale_rain_stats.csv",
        "uv": "app/data/climate_data/daily_uv_stats/salekhard_daily_uv_stats.csv",
        "soil_temp4": "app/data/climate_data/daily_soil_temp_stats/level_4_depth/salekhard_daily_temperature_stats.csv",
        "ssrd": "app/data/climate_data/daily_solar_rad_down_stats/salekhard_daily_surface_solar_rad_stats.csv"
    },
    "southern tundra": {
        "temperature": "app/data/climate_data/daily_temp_stats/saskylakh_daily_temperature_stats.csv",
        "snowfall": "app/data/climate_data/daily_snowfall_stats/saskylakh_daily_snowfall_stats.csv",
        "rainfall": "app/data/climate_data/daily_rainfall_stats/saskylakh_daily_large_scale_rain_stats.csv",
        "uv": "app/data/climate_data/daily_uv_stats/saskylakh_daily_uv_stats.csv",
        "soil_temp4": "app/data/climate_data/daily_soil_temp_stats/level_4_depth/saskylakh_daily_temperature_stats.csv",
        "ssrd": "app/data/climate_data/daily_solar_rad_down_stats/saskylakh_daily_surface_solar_rad_stats.csv"
    },
    "northern tundra": {
        "temperature": "app/data/climate_data/daily_temp_stats/cape_chelyuskin_daily_temperature_stats.csv",
        "snowfall": "app/data/climate_data/daily_snowfall_stats/cape_chelyuskin_daily_snowfall_stats.csv",
        "rainfall": "app/data/climate_data/daily_rainfall_stats/cape_chelyuskin_daily_large_scale_rain_stats.csv",
        "uv": "app/data/climate_data/daily_uv_stats/cape_chelyuskin_daily_uv_stats.csv",
        "soil_temp4": "app/data/climate_data/daily_soil_temp_stats/level_4_depth/cape_chelyuskin_daily_temperature_stats.csv",
        "ssrd": "app/data/climate_data/daily_solar_rad_down_stats/cape_chelyuskin_daily_surface_solar_rad_stats.csv"
    }
}

class Climate:
    """
    Handles all of the climate logic for selecting and running the correct climate driver
    for the corresponding biome and day of the year, and changes in climate conditions based on
    environmental (plot) conditions.
    """
    def __init__(self, biome: str, plot: PlotInformation):
        """
        Initialize a Climate instance.
        
        Args:
            biome (str): The biome type of the plot.
            plot (PlotInformation): The plot information object containing environmental data.
            
        Attributes:
            biome (str): The biome type of the plot.
            plot (PlotInformation): The plot information object containing environmental data.
            loaders (dict): A dictionary to cache climate loaders for different types.
            consecutive_frozen_soil_days (int): Counter for consecutive frozen soil days.
            recent_values (dict): Cache of recent values for fallback when data is None (limited to past week).
        """
        if not isinstance(biome, str):
            raise ValueError(f"Biome must be a string, got: {type(biome)}")
        
        if biome not in BIOME_FILE_MAP:
            raise ValueError(f"Unknown biome: {biome}. Available biomes: {list(BIOME_FILE_MAP.keys())}")
        
        self.biome = biome
        self.plot = plot
        self.loaders = {}
        self.consecutive_frozen_soil_days = 0
        self.recent_values = {
            'temperature': deque(maxlen=7),  # keep last 7 days
            'soil_temp': deque(maxlen=7),
            'snowfall': deque(maxlen=7),
            'rainfall': deque(maxlen=7),
            'uv': deque(maxlen=7),
            'ssrd': deque(maxlen=7)
        }

    def set_biome(self, new_biome: str) -> None:
        """Set the biome for this climate instance."""
        if not isinstance(new_biome, str):
            raise ValueError(f"Biome must be a string, got: {type(new_biome)}")
        
        if new_biome not in BIOME_FILE_MAP:
            raise ValueError(f"Unknown biome: {new_biome}. Available biomes: {list(BIOME_FILE_MAP.keys())}")
        
        logger.info(f"Changing biome from {self.biome} to {new_biome}")
        self.biome = new_biome
        # Clear cached loaders when biome changes
        self.loaders = {}
    
    def get_biome(self) -> str:
        """Get the current biome."""
        return self.biome

    def _load_climate_loader(self, loader_type: str, loader_class) -> object:
        """
        Loads the climate loader for the specified type if not already loaded.
        loader_type (str): The type of climate loader to load (e.g., "temperature", "snowfall", etc.).
        loader_class: The class of the climate loader to instantiate.
        """
        if loader_type not in self.loaders:
            if loader_type not in BIOME_FILE_MAP[self.biome]:
                raise ValueError(f"Unknown loader type '{loader_type}' for biome '{self.biome}'")
            
            filepath = BIOME_FILE_MAP[self.biome][loader_type]
            try:
                self.loaders[loader_type] = loader_class(filepath, self.biome)
                logger.debug(f"Loaded {loader_type} loader for biome {self.biome}")
            except (FileNotFoundError, PermissionError) as e:
                raise RuntimeError(f"Failed to load climate data file for {loader_type}: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error loading climate loader {loader_type}: {e}")
        
        return self.loaders[loader_type]

    def _get_fallback_value(self, data_type: str, day: int) -> Optional[float]:
        """
        Get a fallback value when current data is None.
        Returns the most recent non-None value for this data type from the past week.
        If all recent values are None or no recent values exist, exception raised.
        """
        if data_type not in self.recent_values or not self.recent_values[data_type]:
            raise RuntimeError(f"No recent fallback values available for {data_type} on day {day}")
        
        # Try all values from most recent to oldest
        for value in reversed(list(self.recent_values[data_type])):
            if value is not None:
                logger.warning(f"Using recent fallback value {value} for {data_type} on day {day} (no current data available)")
                return value
        
        # All recent values are None
        raise RuntimeError(f"All recent fallback values for {data_type} on day {day} are None")

    def _update_recent_value(self, data_type: str, value: float) -> None:
        """Update the recent values for a data type."""
        if data_type in self.recent_values:
            self.recent_values[data_type].append(value)

    def get_current_temperature(self, day: int) -> float:
        """
        Returns 2m air temperature as a sum of the random 2m temperature from the 
        regional data for the current day and the change in 2m temperature
        (based on the change in snow depth).

        day (int): The day of the year (1-365).
        returns:
            float: The current temperature for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            delta_snow_height = self.plot.delta_snow_height()
            air_temp_offset = self._2mtemp_change_from_snow_delta(delta_snow_height)

            loader = self._load_climate_loader("temperature", TemperatureLoader)
            driver = TemperatureDriver(loader.get_temp_data())
            result = driver.generate_daily_temp(self.biome, day, air_temp_offset)
            
            if result is None:
                return self._get_fallback_value('temperature', day)
            
            self._update_recent_value('temperature', result)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get temperature for day {day}: {e}")
    
    def get_current_soil_temp(self, day: int) -> float:
        """
        Returns the soil temperature at level 4 depth as a sum of the random soil temperature
        from the regional data for the current day and the change in soil temperature
        (based on the change in snow depth).

        day (int): The day of the year (1-365).
        returns:
            float: The current soil temperature for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            delta_snow_height = self.plot.delta_snow_height()
            soil_temp_offset = self._soil_temp_change_from_snow_delta(delta_snow_height)

            loader = self._load_climate_loader("soil_temp4", SoilTemp4Loader)
            driver = SoilTemp4Driver(loader.get_soil_temp4_data())
            result = driver.generate_daily_soil_temp(self.biome, day, soil_temp_offset)
            
            if result is None:
                return self._get_fallback_value('soil_temp', day)
            
            self._update_recent_value('soil_temp', result)
            self._update_consecutive_frozen_soil_days(result)
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get soil temperature for day {day}: {e}")

    def _update_consecutive_frozen_soil_days(self, soil_temp: float) -> None:
        """
        Update the consecutive frozen soil days counter based on soil temperature.
        """
        if not isinstance(soil_temp, (int, float)):
            logger.warning(f"Invalid soil temperature type: {type(soil_temp)}, expected number")
            return
        
        if soil_temp < 0.0:
            self.consecutive_frozen_soil_days += 1
        else:
            self.consecutive_frozen_soil_days = 0

    def get_current_snowfall(self, day: int) -> float:
        """
        Returns random snowfall for the given day from regional data.

        day (int): The day of the year (1-365).
        returns:
            float: The current snowfall for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            loader = self._load_climate_loader("snowfall", SnowfallLoader)
            driver = SnowfallDriver(loader.get_snowfall_data())
            result = driver.generate_daily_snowfall(self.biome, day)
            
            if result is None:
                return self._get_fallback_value('snowfall', day)
            
            self._update_recent_value('snowfall', result)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get snowfall for day {day}: {e}")

    def get_current_rainfall(self, day: int) -> float:
        """
        Returns random rainfall for the given day from regional data.

        day (int): The day of the year (1-365).
        returns:
            float: The current rainfall for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            loader = self._load_climate_loader("rainfall", RainfallLoader)
            driver = RainfallDriver(loader.get_rainfall_data())
            result = driver.generate_daily_rainfall(self.biome, day)
            
            if result is None:
                return self._get_fallback_value('rainfall', day)
            
            self._update_recent_value('rainfall', result)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get rainfall for day {day}: {e}")

    def get_current_uv(self, day: int) -> float:
        """
        Returns random UV index for the given day from regional data.

        day (int): The day of the year (1-365).
        returns:
            float: The current UV index for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            loader = self._load_climate_loader("uv", UVLoader)
            driver = UVDriver(loader.get_uv_data())
            result = driver.generate_daily_uv(self.biome, day)
            
            if result is None:
                return self._get_fallback_value('uv', day)
            
            self._update_recent_value('uv', result)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get UV for day {day}: {e}")
    
    def get_current_SSRD(self, day: int) -> float:
        """
        Returns random Surface Solar Radiation Downward (SSRD) for the given day
        from regional data.

        day (int): The day of the year (1-365).
        returns:
            float: The SSRD for the given day in the biome.
        """
        if not isinstance(day, int) or day < 1 or day > 365:
            raise ValueError(f"Day must be an integer between 1 and 365, got: {day}")
        
        try:
            loader = self._load_climate_loader("ssrd", SSRDLoader)
            driver = SSRDDriver(loader.get_srd_data())
            result = driver.generate_daily_srd(self.biome, day)
            
            if result is None:
                return self._get_fallback_value('ssrd', day)
            
            self._update_recent_value('ssrd', result)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to get SSRD for day {day}: {e}")
        
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp a value between a min and max."""
        return max(min_value, min(max_value, value))

    @staticmethod
    def _2mtemp_change_from_snow_delta(delta_snow_m: float) -> float:
        """
        Given a change in snow depth.
        return:
        air_temp_change: The change in air temperature at 2 meters above ground level.

        more snow = cools air.
        less snow = warms air.
        """
        raw_air_delta = -delta_snow_m * AIR_SENSITIVITY
        air_temp_delta = Climate.clamp(raw_air_delta, -MAX_DAILY_AIR_DELTA, MAX_DAILY_AIR_DELTA)

        return air_temp_delta
    
    @staticmethod
    def _soil_temp_change_from_snow_delta(delta_snow_m: float) -> float:
        """
        Given a change in snow depth.
        return:
        soil_temp_change: The change in soil temperature at lvl 4 depth below ground.

        more snow = warms soil.
        less snow = cools soil.
        """
        raw_soil_delta = delta_snow_m * SOIL_SENSITIVITY
        soil_temp_delta = Climate.clamp(raw_soil_delta, -MAX_DAILY_SOIL_DELTA, MAX_DAILY_SOIL_DELTA)

        return soil_temp_delta
    
    def is_steppe(self) -> bool:
        """
        Check if the plot is in steppe conditions based on flora mass composition and permafrost.
        Steppe conditions are characterized by high grass ratio, low shrub ratio, and valid permafrost.
        """
        try:
            # Check permafrost conditions
            if not self.is_permafrost():
                logger.warning("Steppe conditions require valid permafrost")
                return False
            
            flora_mass_composition = self.plot.get_flora_mass_composition()
            
            if not flora_mass_composition or len(flora_mass_composition) != 4:
                logger.warning(f"Invalid flora mass composition: {flora_mass_composition}")
                return False
            
            grass_ratio, shrub_ratio, tree_ratio, moss_ratio = flora_mass_composition
            
            # Validate flora ratios
            total_ratio = grass_ratio + shrub_ratio + tree_ratio + moss_ratio
            if abs(total_ratio - 1.0) > 0.01:  # allow small floating point errors
                logger.warning(f"Flora mass ratios don't sum to 1.0, got: {total_ratio}")
                return False
            
            if grass_ratio >= 0.85 and 0.0 <= shrub_ratio <= 0.15:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error determining steppe conditions: {e}")
            return False

    def is_permafrost(self) -> bool:
        """
        Check if the plot is in permafrost conditions based on soil temperature.
        For permafrost to exist, the soil temperature must be below 0.0 degrees Celsius 
        for at least two years in a row.
        Soil level 1 may unthaw (known as the active layer, where grasses survive), 
        but level 4 must remain frozen.
        """
        try:
            # Check consecutive frozen days (720 days = 2 years)
            if self.consecutive_frozen_soil_days >= 720:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error determining permafrost conditions: {e}")
            return False