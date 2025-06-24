# Fauna class represents a flora species within the plot.
# Each Plot will have all Fauna classes that are present in the plot.
# A Fauna class has ideal environmental ranges (i.e. temperature, food, etc)
# The health and survival of the fauna will depend on the distance of the
# current environmental conditions to the ideal ranges.

class Fauna:
    def __init__(self, name: str, description: str, mass: float):
        """
        Represents a fauna species.
        Ideal ranges for temperature, hydration, and food intake
        are hardcoded and determine the conditions for optimal growth or potential death.
        """
        self.name = name
        self.description = description
        self.mass = mass                     # kg
        self.ideal_growth_rate = 0           # kg/day
        self.ideal_temp_range = (0, 0)       # Celsius
        self.ideal_hydration_range = (0, 0)  # kg/day
        self.ideal_food_range = (0, 0)       # kg/day

    def __repr__(self):
        return f"Fauna(name={self.name}, description={self.description}, mass={self.mass})"