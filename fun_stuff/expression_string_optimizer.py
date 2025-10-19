from enum import Enum
from typing import Union


# =============================================================================
# OPERATORS
# =============================================================================

class Operator(Enum):
    pass # subclasses distinguish unary/binary

class UnaryOperator(Operator):
    MINUS = '-'
    BITWISE_NOT = '~'

class BinaryOperator(Operator):
    pass # subclasses distinguish commutative/noncommutative

class BinaryNonCommutativeOperator(BinaryOperator):
    BIT_SHIFT_LEFT = '<<'
    BIT_SHIFT_RIGHT = '>>'
    SUBTRACT = '-'
    EXPONENTIATE = '**'
    INT_DIVIDE = '//'
    MODULO = '%'

class BinaryCommutativeOperator(BinaryOperator):
    ADD = '+'
    MULTIPLY = '*'
    BITWISE_AND = '&'
    BITWISE_OR = '|'
    BITWISE_XOR = '^'


# =============================================================================
# EXPRESSIONS
# =============================================================================

class Expression:
    """A string expression that evaluates to an integer."""

    def __init__(self, string: str) -> None:
        if type(self) is Expression:
            raise TypeError("Expression cannot be instantiated directly.")
        self._string: str = string

    def evaluate(self) -> int:
        """Evaluate the expression and return an integer."""
        return int(eval(self._string))

    def __str__(self):
        return self._string

class TrueExpression(Expression):
    """Base case expression. Evaluates to 1."""

    def __init__(self) -> None:
        super().__init__('True')

class CompositeExpression(Expression):
    """Composite expression, composed of at least one operator and one expression."""

    def __init__(self,
                 operator: Union[UnaryOperator, BinaryOperator],
                 expr_1: Expression,
                 expr_2: Expression = None) -> None:
        """Instantiate a CompositeExpression either from a unary or binary operator."""
        if expr_2 is None:  # Unary operator case
            if not isinstance(operator, UnaryOperator):
                raise TypeError("Operator is binary, but only one expression was given!")
            self._string = f"{operator.value}({expr_1._string})"
        else:  # Binary operator case
            if not isinstance(operator, BinaryOperator):
                raise TypeError("Operator is unary, but two expressions were given!")
            self._string = f"({expr_1._string}) {operator.value} ({expr_2._string})"

        super().__init__(self._string)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    t = TrueExpression()
    print(f"{t} = {t.evaluate()}")

    e1 = CompositeExpression(UnaryOperator.MINUS, t)
    print(f"{e1} = {e1.evaluate()}")

    # FAILS - negative shift count!
    # e2 = CompositeExpression(BinaryNonCommutativeOperator.BIT_SHIFT_LEFT, t, e1)
    # print(f"{e2} = {e2.evaluate()}")

    e2 = CompositeExpression(BinaryNonCommutativeOperator.BIT_SHIFT_LEFT, e1, t)
    print(f"{e2} = {e2.evaluate()}")