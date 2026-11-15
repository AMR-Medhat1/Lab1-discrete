
"""
CS214 Discrete Structures - Lab 1: Inference Rules

Rename this file to lab1_<ID1>_<ID2>.py before submitting.
Keep the class/function names unchanged: your code is tested automatically.
"""


# ======================================================================
# Part 1: Logical Expressions Solver
# ======================================================================
class Expression:
    def __init__(self, representation: str = ""):
        self._representation = ""
        self.set_representation(representation)

    def get_representation(self) -> str:
        return self._representation


    def set_representation(self, representation: str) -> None:
        if not isinstance(representation, str):
            raise ValueError("Representation must be a string")
        self._representation = representation.strip()


class LogicalExpressionSolver:
    # values: e.g. {"P": True, "Q": False, "R": True}
    # raises ValueError for a wrong expression
        # Grammar (lowest to highest precedence):
    #   implies := or ( '>' implies )?        (right-associative)
    #   or      := and ( 'v' and )*
    #   and     := not ( '^' not )*
    #   not     := '~' not | atom
    #   atom    := VARIABLE | '(' implies ')'

    # ---------- public API ----------
    def get_variables(self, expression: Expression) -> list:
        """Parses the expression (raises ValueError if invalid) and
        returns its variables in sorted order."""
        ast = self._parse(expression)
        found = set()
        self._collect(ast, found)
        return sorted(found)

    def evaluate_expression(self, expression: Expression, values: dict) -> bool:
        ast = self._parse(expression)
        return self._eval(ast, values)

    # ---------- tokenizer ----------
    def _tokenize(self, text: str) -> list:
        tokens = []
        for ch in text:
            if ch.isspace():
                continue
            if ch in "()~^v>" or ("A" <= ch <= "Z"):
                tokens.append(ch)
            else:
                raise ValueError(f"Invalid character: {ch!r}")
        return tokens

    # ---------- parser (builds an AST of tuples) ----------
    def _parse(self, expression: Expression):
        text = expression.get_representation()
        if not text:
            raise ValueError("Empty expression")
        self._tokens = self._tokenize(text)
        self._pos = 0
        ast = self._parse_implies()
        if self._pos != len(self._tokens):
            raise ValueError(f"Unexpected token: {self._tokens[self._pos]!r}")
        return ast

    def _peek(self):
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _next(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        self._pos += 1
        return tok

    def _parse_implies(self):
        left = self._parse_or()
        if self._peek() == ">":
            self._next()
            return ("imp", left, self._parse_implies())
        return left

    def _parse_or(self):
        left = self._parse_and()
        while self._peek() == "v":
            self._next()
            left = ("or", left, self._parse_and())
        return left

    def _parse_and(self):
        left = self._parse_not()
        while self._peek() == "^":
            self._next()
            left = ("and", left, self._parse_not())
        return left

    def _parse_not(self):
        if self._peek() == "~":
            self._next()
            return ("not", self._parse_not())
        return self._parse_atom()

    def _parse_atom(self):
        tok = self._next()
        if tok == "(":
            node = self._parse_implies()
            if self._next() != ")":
                raise ValueError("Missing closing parenthesis")
            return node
        if "A" <= tok <= "Z":
            return ("var", tok)
        raise ValueError(f"Unexpected token: {tok!r}")

    # ---------- evaluation ----------
    def _collect(self, node, found: set) -> None:
        if node[0] == "var":
            found.add(node[1])
        else:
            for child in node[1:]:
                self._collect(child, found)

    def _eval(self, node, values: dict) -> bool:
        kind = node[0]
        if kind == "var":
            if node[1] not in values:
                raise ValueError(f"No value for variable {node[1]!r}")
            return bool(values[node[1]])
        if kind == "not":
            return not self._eval(node[1], values)
        a = self._eval(node[1], values)
        b = self._eval(node[2], values)
        if kind == "and":
            return a and b
        if kind == "or":
            return a or b
        if kind == "imp":
            return (not a) or b
        raise ValueError("Unknown node")


# ======================================================================
# Part 2: Inference Engine
# ======================================================================
class InferenceRule:
    def matches(self, exp1: Expression, exp2: Expression) -> bool:
        raise NotImplementedError

    def apply(self, exp1: Expression, exp2: Expression) -> Expression:
        raise NotImplementedError


class ModusPonens(InferenceRule):
    pass  # TODO


class ModusTollens(InferenceRule):
    pass  # TODO


class HypotheticalSyllogism(InferenceRule):
    pass  # TODO


class DisjunctiveSyllogism(InferenceRule):
    pass  # TODO


class Resolution(InferenceRule):
    pass  # TODO


class InferenceEngine:
    def __init__(self):
        pass  # TODO

    def add_rule(self, rule: InferenceRule) -> None:
        raise NotImplementedError  # TODO

    def add_expression(self, exp: Expression) -> None:
        raise NotImplementedError  # TODO

    def apply_rules(self) -> Expression:
        # None if it cannot be inferred
        raise NotImplementedError  # TODO


# returns the program output, e.g. "Y v Z (Resolution)"
def infer(expr1: str, expr2: str) -> str:
    raise NotImplementedError  # TODO


def main():
    pass  # TODO: your program (input / output)


if __name__ == "__main__":
    main()