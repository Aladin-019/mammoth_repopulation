# Flora class represents a flora species within the plot.
# Each Plot will have all Flora classes that are present in the plot.
# A Flora class has ideal environmental ranges (i.e. temperature, UV index, etc)
# The health and survival of the flora will depend on the distance of the
# current environmental conditions to the ideal ranges.

class Flora:
    def __init__(self, name: str, description: str, mass: float):
        """
        Represents a flora species.
        Ideal ranges for temperature, UV index, hydration, and soil temperature
        are hardcoded and determine the conditions for optimal growth or potential death.
        """
        self.name = name
        self.description = description
        self.mass = mass                     # kg
        self.ideal_growth_rate = 0           # kg/day
        self.ideal_temp_range = (0, 0)       # Celsius
        self.ideal_uv_range = (0, 0)         # UV index
        self.ideal_hydration_range = (0, 0)  # kg/day
        self.ideal_soil_temp_range = (0, 0)  # Celsius

    def __repr__(self):
        return f"Flora(name={self.name}, description={self.description}, growth_rate={self.growth_rate})"