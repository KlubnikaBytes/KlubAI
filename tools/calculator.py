
import ast
import operator
import re

from decimal import Decimal, ROUND_HALF_UP


class Calculator:

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    MAX_VALUE = Decimal("1e100")

    @staticmethod
    def normalize(expression):

        expression = expression.strip()

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("^", "**")

        expression = re.sub(
            r"(?<=\d),(?=\d)",
            "",
            expression,
        )

        return expression

    def validate_value(self, value):

        if not value.is_finite():

            raise ValueError(
                "Invalid numerical result."
            )

        if abs(value) > self.MAX_VALUE:

            raise ValueError(
                "Numerical result is too large."
            )

        return value

    def calculate(self, expression):

        expression = self.normalize(expression)

        if not expression:

            raise ValueError(
                "Enter a mathematical expression."
            )

        if len(expression) > 200:

            raise ValueError(
                "Expression is too long."
            )

        try:

            tree = ast.parse(
                expression,
                mode="eval",
            )

        except SyntaxError as error:

            raise ValueError(
                "Invalid mathematical expression."
            ) from error

        if len(list(ast.walk(tree))) > 100:

            raise ValueError(
                "Expression is too complex."
            )

        return self.evaluate_node(tree.body)

    def evaluate_node(self, node):

        if isinstance(node, ast.Constant):

            if type(node.value) not in (int, float):

                raise ValueError(
                    "Only numerical values are allowed."
                )

            return self.validate_value(
                Decimal(str(node.value))
            )

        if isinstance(node, ast.UnaryOp):

            value = self.evaluate_node(node.operand)

            if isinstance(node.op, ast.USub):

                return self.validate_value(-value)

            if isinstance(node.op, ast.UAdd):

                return value

        if isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:

                raise ValueError(
                    "Unsupported mathematical operator."
                )

            left = self.evaluate_node(node.left)
            right = self.evaluate_node(node.right)

            if operator_type in (
                ast.Div,
                ast.FloorDiv,
                ast.Mod,
            ) and right == 0:

                raise ValueError(
                    "Division by zero is not allowed."
                )

            if operator_type is ast.Pow:

                if (
                    abs(right) > 100
                    or right != right.to_integral_value()
                ):

                    raise ValueError(
                        "Only integer exponents between "
                        "-100 and 100 are supported."
                    )

            try:

                result = self.OPERATORS[
                    operator_type
                ](left, right)

            except ArithmeticError as error:

                raise ValueError(
                    "Invalid mathematical operation."
                ) from error

            return self.validate_value(result)

        raise ValueError(
            "Only safe mathematical expressions "
            "are supported."
        )

    @staticmethod
    def format_number(value):

        value = Decimal(str(value))

        if value == 0:
            return "0"

        result = format(value, "f")

        if "." in result:

            result = result.rstrip("0").rstrip(".")

        return result

    @staticmethod
    def money(value):

        return Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def validate_financial_input(self, amount, rate):

        amount = Decimal(str(amount))
        rate = Decimal(str(rate))

        if not amount.is_finite() or not rate.is_finite():

            raise ValueError(
                "Invalid amount or percentage."
            )

        if amount < 0 or amount > Decimal("1e15"):

            raise ValueError(
                "Amount must be between 0 and 10^15."
            )

        if rate < 0 or rate > 100:

            raise ValueError(
                "Percentage must be between 0 and 100."
            )

        return amount, rate

    def percentage(self, rate, amount):

        rate = Decimal(str(rate))
        amount = Decimal(str(amount))

        self.validate_value(rate)
        self.validate_value(amount)

        return self.validate_value(
            amount * rate / Decimal("100")
        )

    def gst(self, amount, rate):

        amount, rate = self.validate_financial_input(
            amount,
            rate,
        )

        amount = self.money(amount)

        tax = self.money(
            amount * rate / Decimal("100")
        )

        total = self.money(amount + tax)

        return {
            "amount": amount,
            "rate": rate,
            "gst": tax,
            "total": total,
        }

    def discount(self, amount, rate):

        amount, rate = self.validate_financial_input(
            amount,
            rate,
        )

        amount = self.money(amount)

        discount_amount = self.money(
            amount * rate / Decimal("100")
        )

        total = self.money(
            amount - discount_amount
        )

        return {
            "amount": amount,
            "rate": rate,
            "discount": discount_amount,
            "total": total,
        }
