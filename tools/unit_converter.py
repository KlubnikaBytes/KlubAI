from decimal import Decimal, localcontext


class UnitConverter:

    UNITS = {

        # Length: base unit metre
        "mm": ("length", "0.001"),
        "cm": ("length", "0.01"),
        "m": ("length", "1"),
        "km": ("length", "1000"),
        "inch": ("length", "0.0254"),
        "ft": ("length", "0.3048"),
        "yard": ("length", "0.9144"),
        "mile": ("length", "1609.344"),

        # Mass: base unit kilogram
        "mg": ("mass", "0.000001"),
        "g": ("mass", "0.001"),
        "kg": ("mass", "1"),
        "tonne": ("mass", "1000"),
        "lb": ("mass", "0.45359237"),
        "oz": ("mass", "0.028349523125"),

        # Time: base unit second
        "second": ("time", "1"),
        "minute": ("time", "60"),
        "hour": ("time", "3600"),
        "day": ("time", "86400"),
        "week": ("time", "604800"),

        # Volume: base unit litre
        "ml": ("volume", "0.001"),
        "l": ("volume", "1"),
        "kl": ("volume", "1000"),
        "gallon": ("volume", "3.785411784"),

        # Area: base unit square metre
        "mm2": ("area", "0.000001"),
        "cm2": ("area", "0.0001"),
        "m2": ("area", "1"),
        "km2": ("area", "1000000"),
        "ft2": ("area", "0.09290304"),
        "acre": ("area", "4046.8564224"),
        "hectare": ("area", "10000"),

        # Decimal digital storage
        "byte": ("data", "1"),
        "kb": ("data", "1000"),
        "mb": ("data", "1000000"),
        "gb": ("data", "1000000000"),
        "tb": ("data", "1000000000000"),

        # Binary digital storage
        "kib": ("data", "1024"),
        "mib": ("data", "1048576"),
        "gib": ("data", "1073741824"),
        "tib": ("data", "1099511627776"),
    }

    TEMPERATURE_UNITS = {
        "c",
        "f",
        "k",
    }

    ALIASES = {

        "millimeter": "mm",
        "millimeters": "mm",
        "millimetre": "mm",
        "millimetres": "mm",

        "centimeter": "cm",
        "centimeters": "cm",
        "centimetre": "cm",
        "centimetres": "cm",

        "meter": "m",
        "meters": "m",
        "metre": "m",
        "metres": "m",

        "kilometer": "km",
        "kilometers": "km",
        "kilometre": "km",
        "kilometres": "km",

        "in": "inch",
        "inches": "inch",
        "foot": "ft",
        "feet": "ft",
        "yards": "yard",
        "miles": "mile",

        "milligram": "mg",
        "milligrams": "mg",
        "gram": "g",
        "grams": "g",
        "kilogram": "kg",
        "kilograms": "kg",
        "tonnes": "tonne",
        "pound": "lb",
        "pounds": "lb",
        "ounce": "oz",
        "ounces": "oz",

        "sec": "second",
        "seconds": "second",
        "min": "minute",
        "minutes": "minute",
        "hr": "hour",
        "hours": "hour",
        "days": "day",
        "weeks": "week",

        "milliliter": "ml",
        "milliliters": "ml",
        "millilitre": "ml",
        "millilitres": "ml",
        "liter": "l",
        "liters": "l",
        "litre": "l",
        "litres": "l",
        "gallons": "gallon",

        "square meter": "m2",
        "square meters": "m2",
        "square metre": "m2",
        "square metres": "m2",
        "square feet": "ft2",
        "square foot": "ft2",
        "square kilometer": "km2",
        "square kilometers": "km2",
        "acres": "acre",
        "hectares": "hectare",

        "bytes": "byte",
        "kilobyte": "kb",
        "kilobytes": "kb",
        "megabyte": "mb",
        "megabytes": "mb",
        "gigabyte": "gb",
        "gigabytes": "gb",
        "terabyte": "tb",
        "terabytes": "tb",

        "celsius": "c",
        "fahrenheit": "f",
        "kelvin": "k",
        "°c": "c",
        "°f": "f",
    }

    def normalize_unit(self, unit):

        unit = unit.strip().lower()

        unit = unit.replace("â°", "°").replace("â²", "²")
        unit = unit.replace("²", "2")
        unit = unit.replace("^2", "2")

        unit = " ".join(unit.split())

        return self.ALIASES.get(unit, unit)

    def convert(self, value, from_unit, to_unit):

        value = Decimal(str(value))

        if not value.is_finite():

            raise ValueError("Invalid numerical value.")

        if abs(value) > Decimal("1e30"):

            raise ValueError("Numerical value is too large.")

        source = self.normalize_unit(from_unit)
        target = self.normalize_unit(to_unit)

        with localcontext() as context:

            context.prec = 40

            if (
                source in self.TEMPERATURE_UNITS
                and target in self.TEMPERATURE_UNITS
            ):

                return self.convert_temperature(
                    value,
                    source,
                    target,
                )

            if source not in self.UNITS:

                raise ValueError(
                    f"Unsupported source unit: {from_unit}"
                )

            if target not in self.UNITS:

                raise ValueError(
                    f"Unsupported target unit: {to_unit}"
                )

            source_category, source_factor = (
                self.UNITS[source]
            )

            target_category, target_factor = (
                self.UNITS[target]
            )

            if source_category != target_category:

                raise ValueError(
                    "Cannot convert between "
                    "different measurement categories."
                )

            result = (
                value
                * Decimal(source_factor)
                / Decimal(target_factor)
            )

            return result

    def convert_temperature(
        self,
        value,
        source,
        target,
    ):

        # Convert to Celsius first.
        if source == "c":

            celsius = value

        elif source == "f":

            celsius = (
                (value - Decimal("32"))
                * Decimal("5")
                / Decimal("9")
            )

        else:

            celsius = value - Decimal("273.15")

        if celsius < Decimal("-273.15"):

            raise ValueError(
                "Temperature cannot be below absolute zero."
            )

        if source == target:

            return value

        if target == "c":

            return celsius

        if target == "f":

            return (
                celsius
                * Decimal("9")
                / Decimal("5")
                + Decimal("32")
            )

        return celsius + Decimal("273.15")

    @staticmethod
    def format_number(value):

        if value == 0:

            return "0"

        # Display up to 12 significant digits.
        result = format(value, ".12g")

        # Keep extreme values compact to avoid enormous strings.
        if -12 <= Decimal(result).adjusted() <= 30:
            result = format(Decimal(result), "f")

        if "e" not in result.lower() and "." in result:

            result = result.rstrip("0").rstrip(".")

        return result

    def get_supported_units(self):

        return (
            "Supported Unit Conversions\n\n"
            "Length: mm, cm, m, km, inch, ft, yard, mile\n"
            "Mass: mg, g, kg, tonne, lb, oz\n"
            "Temperature: Celsius, Fahrenheit, Kelvin\n"
            "Time: second, minute, hour, day, week\n"
            "Volume: ml, l, kl, US gallon\n"
            "Area: mm2, cm2, m2, km2, ft2, acre, hectare\n"
            "Data: byte, KB, MB, GB, TB\n"
            "Binary Data: KiB, MiB, GiB, TiB\n\n"
            "1 GB = 1000 MB\n"
            "1 GiB = 1024 MiB\n"
            "Gallon means US liquid gallon."
        )
