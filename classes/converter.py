from typing import Literal

from modules.commons import convert_float_to_time


class Length:
    """Class to convert length units"""
    imperial_units: dict[str, float] = {
        "thou": 0.001,
        "inch": 1,
        "foot": 12,
        "yard": 36,
        "mile": 63_360,
        "league": 190_080,
        "fathom": 72,
        "chain": 792,
        "rod": 198,
        "banana": 7.5,
        "football_field": 3_600,
    }
    """Dictionary of imperial units and their conversion to inches"""
    metric_units: dict[str, float] = {
        "millimeter": 0.001,
        "centimeter": 0.01,
        "decimeter": 0.1,
        "meter": 1,
        "decameter": 10,
        "hectometer": 100,
        "kilometer": 1_000,
        "nautical_mile": 1_852,
        "myriameter": 10_000,
        "earth_radius": 6_371_000,
        "ligth_second": 299_792_458,
        "lunar_distance": 384_402_000,
        "astronomical_unit": 149_597_870_700,
        "light_year": 9_460_730_472_580_800,
    }
    """Dictionary of metric units and their conversion to meters"""
    inch_to_meter = 0.0254
    """Conversion factor from inches to meters"""

    @staticmethod
    def convert(
        value: float,
        from_unit: Literal[
            "astronomical_unit",
            "banana",
            "centimeter",
            "chain",
            "decameter",
            "decimeter",
            "earth_radius",
            "fathom",
            "foot",
            "football_field",
            "hectometer",
            "inch",
            "kilometer",
            "league",
            "light_year",
            "ligth_second",
            "lunar_distance",
            "meter",
            "mile",
            "millimeter",
            "myriameter",
            "nautical_mile",
            "rod",
            "thou",
            "yard",
        ],
        to_unit: Literal[
            "banana",
            "centimeter",
            "chain",
            "decameter",
            "decimeter",
            "fathom",
            "foot",
            "football_field",
            "hectometer",
            "inch",
            "kilometer",
            "league",
            "meter",
            "mile",
            "millimeter",
            "myriameter",
            "nautical_mile",
            "rod",
            "thou",
            "yard",
        ],
    ) -> float:
        """
        Converts a length from one unit to another

        Args:
            value (float): Amount of length to convert
            from_unit (Literal["banana", "centimeter", "chain", "decameter", "decimeter", "earth_radius", "fathom", "foot", "football_field", "hectometer", "inch", "kilometer", "league", "light_year", "ligth_second", "lunar_distance", "meter", "mile", "millimeter", "myriameter", "nautical_mile", "rod", "thou", "yard"]): Unit to convert the value from
            to_unit (Literal["banana", "centimeter", "chain", "decameter", "decimeter", "fathom", "foot", "football_field", "hectometer", "inch", "kilometer", "league", "meter", "mile", "millimeter", "myriameter", "nautical_mile", "rod", "thou", "yard"]): Unit to convert the value to

        Returns:
            float: Converted value
        """
        if from_unit in Length.imperial_units and to_unit in Length.imperial_units:
            base_value = value * Length.imperial_units[from_unit]
            converted_value = base_value / Length.imperial_units[to_unit]
        elif from_unit in Length.metric_units and to_unit in Length.metric_units:
            base_value = value * Length.metric_units[from_unit]
            converted_value = base_value / Length.metric_units[to_unit]
        else:
            total_inches = value * Length.imperial_units[from_unit]
            total_meters = total_inches * Length.inch_to_meter
            converted_value = total_meters / Length.metric_units[to_unit]

        return converted_value


class Temperature:
    """Class to convert temperature units"""
    conversions = {
        "celsius": {
            "kelvin": lambda t: t + 273.15,
            "fahrenheit": lambda t: (t * 9 / 5) + 32,
            "reaumur": lambda t: t * 4 / 5,
            "romer": lambda t: (t * 21 / 40) + 7.5,
            "newton": lambda t: t * 33 / 100,
            "delisle": lambda t: (100 - t) * 3 / 2
        },
        "kelvin": {
            "celsius": lambda t: t - 273.15,
            "fahrenheit": lambda t: (t * 9 / 5) - 459.67,
            "reaumur": lambda t: (t - 273.15) * 4 / 5,
            "romer": lambda t: ((t - 273.15) * 21 / 40) + 7.5,
            "newton": lambda t: (t - 273.15) * 33 / 100,
            "delisle": lambda t: (373.15 - t) * 3 / 2
        },
        "fahrenheit": {
            "celsius": lambda t: (t - 32) * 5 / 9,
            "kelvin": lambda t: (t + 459.67) * 5 / 9,
            "reaumur": lambda t: (t - 32) * 4 / 9,
            "romer": lambda t: ((t - 32) * 7 / 24) + 7.5,
            "newton": lambda t: (t - 32) * 11 / 60,
            "delisle": lambda t: (212 - t) * 5 / 6
        },
        "reaumur": {
            "celsius": lambda t: t * 5 / 4,
            "kelvin": lambda t: (t * 5 / 4) + 273.15,
            "fahrenheit": lambda t: (t * 9 / 4) + 32,
            "romer": lambda t: (t * 21 / 32) + 7.5,
            "newton": lambda t: (t * 33 / 80),
            "delisle": lambda t: (80 - t) * 15 / 8
        },
        "romer": {
            "celsius": lambda t: (t - 7.5) * 40 / 21,
            "kelvin": lambda t: ((t - 7.5) * 40 / 21) + 273.15,
            "fahrenheit": lambda t: ((t - 7.5) * 24 / 7) + 32,
            "reaumur": lambda t: (t - 7.5) * 32 / 21,
            "newton": lambda t: (t - 7.5) * 22 / 35,
            "delisle": lambda t: (60 - t) * 20 / 7
        },
        "newton": {
            "celsius": lambda t: t * 100 / 33,
            "kelvin": lambda t: (t * 100 / 33) + 273.15,
            "fahrenheit": lambda t: (t * 60 / 11) + 32,
            "reaumur": lambda t: t * 80 / 33,
            "romer": lambda t: (t * 35 / 22) + 7.5,
            "delisle": lambda t: (33 - t) * 50 / 11
        },
        "delisle": {
            "celsius": lambda t: 100 - (t * 2 / 3),
            "kelvin": lambda t: 373.15 - (t * 2 / 3),
            "fahrenheit": lambda t: 212 - (t * 6 / 5),
            "reaumur": lambda t: (80 - t) * 8 / 15,
            "romer": lambda t: (60 - t) * 7 / 20,
            "newton": lambda t: (33 - t) * 11 / 50
        }
    }

    @staticmethod
    def convert(
        value: float,
        from_unit: Literal[
            "celsius",
            "kelvin",
            "fahrenheit",
            "reaumur",
            "romer",
            "newton",
            "delisle"
        ],
        to_unit: Literal[
            "celsius",
            "kelvin",
            "fahrenheit",
            "reaumur",
            "romer",
            "newton",
            "delisle"
        ],
    ) -> float:
        """
        Converts temperature from one unit to another

        Args:
            value (float): The value of temperature to convert
            from_unit (Literal["celsius", "kelvin", "fahrenheit", "reaumur", "romer", "newton", "delisle"]): The unit to convert from
            to_unit (Literal["celsius", "kelvin", "fahrenheit", "reaumur", "romer", "newton", "delisle"]): The unit to convert to

        Raises:
            ValueError: If the units are not valid

        Returns:
            float: The converted temperature
        """
        if from_unit in Temperature.conversions and to_unit in Temperature.conversions[from_unit]:
            conversion_fn = Temperature.conversions[from_unit][to_unit]
            return conversion_fn(value)
        raise ValueError("Invalid temperature conversion units")


class Mass:
    """Class to convert mass units"""
    imperial_units: dict[str, float] = {
        "ounce": 0.0625,
        "pound": 1,
        "stone": 14,
        "quarter": 28,
        "hundredweight": 112,
        "ton": 2240,
    }
    """Dictionary of imperial units and their conversion to pounds"""

    metric_units: dict[str, float] = {
        "milligram": 0.000001,
        "centigram": 0.00001,
        "decigram": 0.0001,
        "gram": 0.001,
        "decagram": 0.01,
        "hectogram": 0.1,
        "kilogram": 1,
        "metric_ton": 1000,
    }
    """Dictionary of metric units and their conversion to kilograms"""

    pound_to_kilogram = 0.453592
    """Conversion factor from pounds to kilograms"""

    @staticmethod
    def convert(
        value: float,
        from_unit: Literal[
            "centigram",
            "decagram",
            "decigram",
            "gram",
            "hectogram",
            "hundredweight",
            "kilogram",
            "metric_ton",
            "milligram",
            "ounce",
            "pound",
            "quarter",
            "stone",
            "ton",
        ],
        to_unit: Literal[
            "centigram",
            "decagram",
            "decigram",
            "gram",
            "hectogram",
            "hundredweight",
            "kilogram",
            "metric_ton",
            "milligram",
            "ounce",
            "pound",
            "quarter",
            "stone",
            "ton",
        ],
    ) -> float:
        """
        Converts mass from one unit to another. Imperial units are based on US units.

        Args:
            value (float): The value of mass to convert
            from_unit (Literal["centigram", "decagram", "decigram", "gram", "hectogram", "hundredweight", "kilogram", "metric_ton", "milligram", "ounce", "pound", "quarter", "stone", "ton"]): The unit to convert from
            to_unit (Literal["centigram", "decagram", "decigram", "gram", "hectogram", "hundredweight", "kilogram", "metric_ton", "milligram", "ounce", "pound", "quarter", "stone", "ton"]): The unit to convert to

        Returns:
            float: The converted mass
        """
        if from_unit in Mass.imperial_units and to_unit in Mass.imperial_units:
            base_value = value * Mass.imperial_units[from_unit]
            converted_value = base_value / Mass.imperial_units[to_unit]
        elif from_unit in Mass.metric_units and to_unit in Mass.metric_units:
            base_value = value * Mass.metric_units[from_unit]
            converted_value = base_value / Mass.metric_units[to_unit]
        else:
            total_pounds = value * Mass.imperial_units[from_unit]
            total_kilograms = total_pounds * Mass.pound_to_kilogram
            converted_value = total_kilograms / Mass.metric_units[to_unit]

        return converted_value


class Volume:
    """Class to convert volume units"""
    imperial_units: dict[str, float] = {
        "teaspoon": 1,
        "tablespoon": 3,
        "fluid_ounce": 6,
        "gill": 24,
        "cup": 48,
        "pint": 96,
        "quart": 192,
        "gallon": 768,
    }
    """Dictionary of imperial units and their conversion to teaspoons"""

    metric_units: dict[str, float] = {
        "milliliter": 1,
        "centiliter": 10,
        "deciliter": 100,
        "liter": 1000,
        "decaliter": 10000,
        "hectoliter": 100000,
        "kiloliter": 1000000,
    }
    """Dictionary of metric units and their conversion to milliliters"""

    teaspoon_to_milliliter = 4.92892
    """Conversion factor from teaspoons to milliliters"""

    @staticmethod
    def convert(
        value: float,
        from_unit: Literal[
            "centiliter",
            "decaliter",
            "deciliter",
            "fluid_ounce",
            "gallon",
            "gill",
            "hectoliter",
            "kiloliter",
            "liter",
            "milliliter",
            "pint",
            "quart",
            "tablespoon",
            "teaspoon",
        ],
        to_unit: Literal[
            "centiliter",
            "decaliter",
            "deciliter",
            "fluid_ounce",
            "gallon",
            "gill",
            "hectoliter",
            "kiloliter",
            "liter",
            "milliliter",
            "pint",
            "quart",
            "tablespoon",
            "teaspoon",
        ],
    ) -> float:
        """
        Converts volume from one unit to another. Imperial units are based on US customary units.

        Args:
            value (float): The value of volume to convert
            from_unit (Literal["centiliter", "decaliter", "deciliter", "fluid_ounce", "gallon", "gill", "hectoliter", "kiloliter", "liter", "milliliter", "pint", "quart", "tablespoon", "teaspoon"]): The unit to convert from
            to_unit (Literal["centiliter", "decaliter", "deciliter", "fluid_ounce", "gallon", "gill", "hectoliter", "kiloliter", "liter", "milliliter", "pint", "quart", "tablespoon", "teaspoon"]): The unit to convert to

        Returns:
            float: The converted volume
        """
        if from_unit in Volume.imperial_units and to_unit in Volume.imperial_units:
            base_value = value * Volume.imperial_units[from_unit]
            converted_value = base_value / Volume.imperial_units[to_unit]
        elif from_unit in Volume.metric_units and to_unit in Volume.metric_units:
            base_value = value * Volume.metric_units[from_unit]
            converted_value = base_value / Volume.metric_units[to_unit]
        else:
            total_teaspoons = value * Volume.imperial_units[from_unit]
            total_milliliters = total_teaspoons * Volume.teaspoon_to_milliliter
            converted_value = total_milliliters / Volume.metric_units[to_unit]

        return converted_value


class Time:
    """Class to convert time units"""
    conversion_factors = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
        "years": 31536000,
        "decades": 315360000,
        "generations": 630720000,
        "centuries": 3153600000,
        "millennia": 31536000000,
        "eon": 3153600000000000000,
    }
    """Dictionary of time units and their conversion to seconds"""

    @staticmethod
    def convert(
        value: float,
        from_unit: Literal[
            "seconds", "minutes", "hours", "days", "weeks", "years", "decades", "generations", "centuries", "millennia", "eon"
        ],
        to_unit: Literal[
            "seconds", "minutes", "hours", "days", "weeks", "years", "decades", "generations", "centuries"
        ],
    ) -> list[float | str]:
        """
        Converts time from one unit to another.

        Args:
            value (float): The value of time to convert
            from_unit (Literal["seconds", "minutes", "hours", "days", "weeks", "years", "decades", "generations", "centuries", "millenia", "eon"]): The unit to convert from
            to_unit (Literal["seconds", "minutes", "hours", "days", "weeks", "years", "decades", "generations", "centuries"]): The unit to convert to

        Returns:
            list[float | str]: The converted time and the context of the conversion
        """
        days_total = value * \
            (Time.conversion_factors[from_unit] /
             Time.conversion_factors["days"])
        context = convert_float_to_time(days_total, show_weeks=True)
        if from_unit in Time.conversion_factors and to_unit in Time.conversion_factors:
            converted_value = value * \
                (Time.conversion_factors[from_unit] /
                 Time.conversion_factors[to_unit])
        else:
            converted_value = value  # Conversion between the same units

        return [converted_value, context]
