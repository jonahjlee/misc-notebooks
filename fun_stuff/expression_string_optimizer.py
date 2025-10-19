import copy
import warnings
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

    def __init__(self, string: str, score: int) -> None:
        if type(self) is Expression:
            raise TypeError("Expression cannot be instantiated directly.")
        self._string: str = string
        self._score: int = score

    def evaluate(self) -> int:
        """Evaluate the expression and return an integer."""
        return int(eval(self._string))

    def __str__(self):
        return self._string

    @property
    def string(self) -> str:
        return self._string

    @property
    def score(self) -> int:
        return self._score

class TrueExpression(Expression):
    """Base case expression. Evaluates to 1."""

    def __init__(self) -> None:
        super().__init__('True', 1)

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
            string = f"{operator.value}({expr_1._string})"
            score = expr_1.score + 1
        else:  # Binary operator case
            if not isinstance(operator, BinaryOperator):
                raise TypeError("Operator is unary, but two expressions were given!")
            string = f"({expr_1._string}){operator.value}({expr_2._string})"
            score = expr_1.score + expr_2.score + 1

        super().__init__(string, score)


# =============================================================================
# OPTIMIZER
# =============================================================================

class ExpressionOptimizer:
    def __init__(self):
        # ExpressionOptimizer contains an expression for all targets which can
        # be reached with a score less than or equal to `_max_score`
        self._max_score: int = 1

        # Map of score to list of expressions with that score
        # Each expression in the list must have a different target,
        # and a target will only be found once in the entire dictionary
        self._min_s_exprs: dict[int, list[Expression]] = {
            1: [TrueExpression()]
        }

        # Map of targets to min-s expression with that target
        self._targs: dict[int, Expression] = {
            1: TrueExpression()
        }

    def _get_score_exprs(self, score: int) -> list[Expression]:
        return self._min_s_exprs[score]

    def _add_expr_if_better(self, expr: Expression) -> bool:
        if expr.evaluate() in self._targs.keys():
            # An equal or better expression was already found
            return False

        # New target reached!
        self._targs[expr.evaluate()] = expr
        self._min_s_exprs[expr.score] = self._min_s_exprs.get(expr.score, []) + [expr]

        return True

    def get_min_s_exprs(self):
        return copy.deepcopy(self._min_s_exprs)

    def get_targ_exprs(self):
        return copy.deepcopy(self._targs)

    def print_score_exprs(self, score: int):
        expr_list = self._get_score_exprs(score)
        score_formatter = "{:0>" + str(len(str(self._max_score))) + "}"
        for expr in expr_list:
            try:
                value_str = str(expr.evaluate())
            except ValueError:
                value_str = "Too large to print!"

            # print(f"Score: {score_formatter.format(score)}, "
            #       f"Target: {value_str}, Expression: {expr.string}")
            print(f"Score {score_formatter.format(score)}: "
                  f"{expr.string} = {value_str}")


    def print_min_s_exprs(self):
        for score in range(1, self._max_score + 1):
            self.print_score_exprs(score)

    def print_newest_exprs(self):
        self.print_score_exprs(self._max_score)

    @property
    def max_score(self):
        return self._max_score

    def increase_max_score(self) -> int:
        """
        Increase the maximum allowed score of the expressions.
        Returns the number of new targets reached.
        """
        # Search for composite expressions that will have a score of max_score + 1
        new_exprs = []

        # Unary operators
        for expr in self._get_score_exprs(self._max_score):
            for op in UnaryOperator:
                new_exprs.append(CompositeExpression(op, expr))

        # Binary non-commutative operators
        for score_1 in range(1, self._max_score):
            score_2 = self._max_score - score_1
            # score_1 + score_2 + 1 = max_score + 1

            # Iterate over all pairs of expressions which yield expressions
            # with a score of max_score + 1 when combined via a binary operator
            for expr_1 in self._get_score_exprs(score_1):
                for expr_2 in self._get_score_exprs(score_2):

                    if expr_1.evaluate() <= expr_2.evaluate():
                        # Commutative operators (no need calculate both ways)
                        for op in BinaryCommutativeOperator:
                            new_exprs.append(CompositeExpression(op, expr_1, expr_2))

                    # Non-commutative operators
                    for op in BinaryNonCommutativeOperator:

                        if ((op in [BinaryNonCommutativeOperator.BIT_SHIFT_LEFT,
                            BinaryNonCommutativeOperator.BIT_SHIFT_RIGHT])
                            and expr_2.evaluate()) <= 0:
                            # Cannot bit-shift by negative value,
                            # and bit-shift by zero is pointless
                            continue

                        new_exprs.append(CompositeExpression(op, expr_1, expr_2))

        for new_expr in new_exprs:
            self._add_expr_if_better(new_expr)

        self._max_score += 1

        return len(self._get_score_exprs(self._max_score))


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Python doesn't like it when you do ~True, because it thinks you're doing it by mistake! I am not.
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    optimizer = ExpressionOptimizer()
    for i in range(100):
        try:
            optimizer.get_min_s_exprs()
            optimizer.print_newest_exprs()
            optimizer.increase_max_score()
        except OverflowError:
            break

    for targ in sorted(list(optimizer.get_targ_exprs())):
        try:
            print(targ)
        except ValueError:
            print("Too large to print!")