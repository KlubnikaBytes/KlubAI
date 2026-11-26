
import re

from tools.calculator import Calculator


class TaskRouter:

    NUMBER = r"\d[\d,]*(?:\.\d+)?"

    def __init__(self):

        self.calculator = Calculator()

    @staticmethod
    def clean_number(value):

        return value.replace(",", "").strip()

    def get_help(self):

        return (
            "KlubAI Intelligent Task Commands\n\n"
            "/calculate 25 * 16\n"
            "/gst 25000 18\n"
            "/discount 5000 15\n"
            "/percentage 25 15000\n\n"
            "Natural language examples:\n"
            "Calculate 254 x 876\n"
            "Calculate 18% GST on 25000\n"
            "Apply 15% discount on 5000\n"
            "Calculate 25% of 15000\n"
            "What is 100 / 5?\n\n"
            "GST and discount commands use:\n"
            "Amount followed by percentage.\n\n"
            "Percentage command uses:\n"
            "Percentage followed by amount."
        )

    def format_gst(self, amount, rate):

        result = self.calculator.gst(
            amount,
            rate,
        )

        return (
            "GST Calculation\n\n"
            f"Base Amount: INR {result['amount']:,.2f}\n"
            f"GST Rate: {result['rate']}%\n"
            f"GST Amount: INR {result['gst']:,.2f}\n"
            f"Total Amount: INR {result['total']:,.2f}\n\n"
            "Calculated locally by KlubAI."
        )

    def format_discount(self, amount, rate):

        result = self.calculator.discount(
            amount,
            rate,
        )

        return (
            "Discount Calculation\n\n"
            f"Original Amount: INR {result['amount']:,.2f}\n"
            f"Discount Rate: {result['rate']}%\n"
            f"Discount Amount: INR {result['discount']:,.2f}\n"
            f"Final Amount: INR {result['total']:,.2f}\n\n"
            "Calculated locally by KlubAI."
        )

    def format_percentage(self, rate, amount):

        result = self.calculator.percentage(
            rate,
            amount,
        )

        return (
            f"{rate}% of {amount} = "
            f"{self.calculator.format_number(result)}"
        )

    def route(self, message):

        message = message.strip()

        command = message.lower()

        if command in (
            "/task-help",
            "show task commands",
        ):

            return self.get_help()

        if command.startswith("/calculate "):

            expression = message.split(
                maxsplit=1
            )[1]

            result = self.calculator.calculate(
                expression
            )

            return (
                f"Result: "
                f"{self.calculator.format_number(result)}"
            )

        for prefix in (
            "/gst",
            "/discount",
            "/percentage",
        ):

            if (
                command == prefix
                or command.startswith(prefix + " ")
            ):

                parts = message.split()

                if len(parts) != 3:

                    return (
                        f"Invalid command.\n"
                        f"Type /task-help for examples."
                    )

                first = self.clean_number(parts[1])
                second = self.clean_number(parts[2])

                if prefix == "/gst":

                    return self.format_gst(
                        first,
                        second,
                    )

                if prefix == "/discount":

                    return self.format_discount(
                        first,
                        second,
                    )

                return self.format_percentage(
                    first,
                    second,
                )

        text = command.rstrip("?!.").strip()

        text = text.replace("₹", "")
        text = re.sub(r"\binr\b", "", text)
        text = re.sub(r"\brs\.?\s*", "", text)
        text = re.sub(r"\s+", " ", text)

        number = self.NUMBER

        gst_pattern = (
            rf"^(?:calculate\s+)?"
            rf"({number})\s*%\s*gst\s+"
            rf"(?:on|of)\s+({number})$"
        )

        match = re.fullmatch(
            gst_pattern,
            text,
        )

        if match:

            rate = self.clean_number(match.group(1))
            amount = self.clean_number(match.group(2))

            return self.format_gst(
                amount,
                rate,
            )

        discount_pattern = (
            rf"^(?:(?:apply|calculate)\s+)?"
            rf"({number})\s*%\s*discount\s+"
            rf"(?:on|of)\s+({number})$"
        )

        match = re.fullmatch(
            discount_pattern,
            text,
        )

        if match:

            rate = self.clean_number(match.group(1))
            amount = self.clean_number(match.group(2))

            return self.format_discount(
                amount,
                rate,
            )

        percentage_pattern = (
            rf"^(?:(?:calculate|what is)\s+)?"
            rf"({number})\s*%\s*of\s+"
            rf"({number})$"
        )

        match = re.fullmatch(
            percentage_pattern,
            text,
        )

        if match:

            rate = self.clean_number(match.group(1))
            amount = self.clean_number(match.group(2))

            return self.format_percentage(
                rate,
                amount,
            )

        expression = re.sub(
            r"^(?:calculate|compute|what is|solve)\s+",
            "",
            text,
        )

        expression = re.sub(
            r"(?<=\d)\s*x\s*(?=\d)",
            "*",
            expression,
        )

        if (
            re.fullmatch(
                r"[\d\s.,+\-*/%()^×÷−]+",
                expression,
            )
            and any(
                symbol in expression
                for symbol in "+-*/%^×÷−"
            )
        ):

            result = self.calculator.calculate(
                expression
            )

            return (
                f"{expression} = "
                f"{self.calculator.format_number(result)}"
            )

        return None
