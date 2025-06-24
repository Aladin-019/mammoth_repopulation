class Flora:
    def __init__(self, name: str, description: str, growth_rate: float, mass: float):
        """
        Represents a flora species in the mammoth repopulation project.
        ideal ranges for temperature, UV index, hydration, and soil temperature
        are hardcoded and determine the conditions for optimal growth or potential death.
        """
        self.name = name
        self.description = description
        self.growth_rate = growth_rate       # kg/day
        self.mass = mass                     # kg
        self.ideal_temp_range = (0, 0)       # Celsius
        self.ideal_uv_range = (0, 0)         # UV index
        self.ideal_hydration_range = (0, 0)  # kg
        self.ideal_soil_temp_range = (0, 0)  # Celsius

    def __repr__(self):
        return f"Flora(name={self.name}, description={self.description}, growth_rate={self.growth_rate})"