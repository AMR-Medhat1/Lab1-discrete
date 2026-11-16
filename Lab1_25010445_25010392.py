
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

    # public methods
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

    #  tokenizer 
    def _tokenize(self, text: str) -> list:
        tokens = []
        for ch in text:
            if ch.isspace():
                continue
            if ch in "()~^v>" or ( ch.isalpha() and ch != "v"):
                tokens.append(ch)
            else:
                raise ValueError(f"Invalid character: {ch!r}")
        return tokens

    # parser
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
        left = self._parse_or_and()
        if self._peek() == ">":
            self._next()
            return ("imp", left, self._parse_implies())
        return left

    def _parse_or_and(self):
        left = self._parse_not()
        op = None
        while self._peek() in ("^", "v"):
            tok = self._next()
            if op is not None and tok != op:
                raise ValueError("Mixing ^ and v needs brackets") 
            
            op = tok
            left = ("and" if op =="^" else "or", left, self._parse_not())
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

    # evaluation
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
        # returns a string with no spaces 
    def clean(self, exp: Expression) -> str:
        return exp.get_representation().replace(" ", "")

        # splits text aroud ^ or v
    def split(self, text: str):
        for op in (">", "v"):
            if op in text:
                left, right = text.split(op)
                return left, op, right
        return text, None, None

    
    def negate(self, text: str) -> str:
        if text.startswith("~"):
            return text[1:]
        return "~" + text

        # Try the pair in both orders. Return the inferred Expression, or None.
    def find(self, exp1: Expression, exp2: Expression):
        first, second = self.clean(exp1), self.clean(exp2)
        for a, b in ((first, second), (second, first)):
            result = self.try_rule(a, b)
            if result is not None:
                return Expression(result)
        return None

        # each rule overrides this: returns the result text, or None
    def try_rule(self, a: str, b: str):
        raise NotImplementedError
    
    def matches(self, exp1: Expression, exp2: Expression) -> bool:
        raise NotImplementedError

    def apply(self, exp1: Expression, exp2: Expression) -> Expression:
        raise NotImplementedError


class ModusPonens(InferenceRule):
    # P > Q  and  P   implies  Q
    def try_rule(self, a, b):
        left, op, right = self.split(a)
        if op == ">" and b == left:
            return right
        return None

    def matches(self, exp1, exp2):
        return self.find(exp1, exp2) is not None

    def apply(self, exp1, exp2):
        return self.find(exp1, exp2)


class ModusTollens(InferenceRule):
    # P > Q  and  ~Q   implies  ~P
    def try_rule(self, a, b):
        left, op, right = self.split(a)
        if op == ">" and b == self.negate(right):
            return self.negate(left)
        return None

    def matches(self, exp1, exp2):
        return self.find(exp1, exp2) is not None

    def apply(self, exp1, exp2):
        return self.find(exp1, exp2)


class HypotheticalSyllogism(InferenceRule):
    # P > Q  and  Q > R   implies  P > R
    def try_rule(self, a, b):
        left1, op1, right1 = self.split(a)
        left2, op2, right2 = self.split(b)
        if op1 == ">" and op2 == ">" and right1 == left2:
            return left1 + " > " + right2
        return None

    def matches(self, exp1, exp2):
        return self.find(exp1, exp2) is not None

    def apply(self, exp1, exp2):
        return self.find(exp1, exp2)


class DisjunctiveSyllogism(InferenceRule):
    # P v Q  and  ~P   implies  Q
    def try_rule(self, a, b):
        left, op, right = self.split(a)
        if op == "v" and b == self.negate(left):
            return right
        return None

    def matches(self, exp1, exp2):
        return self.find(exp1, exp2) is not None

    def apply(self, exp1, exp2):
        return self.find(exp1, exp2)


class Resolution(InferenceRule):
    # P v Q  and  ~P v R   implies  Q v R
    def try_rule(self, a, b):
        left1, op1, right1 = self.split(a)
        left2, op2, right2 = self.split(b)
        if op1 == "v" and op2 == "v" and left2 == self.negate(left1):
            return right1 + " v " + right2
        return None

    def matches(self, exp1, exp2):
        return self.find(exp1, exp2) is not None

    def apply(self, exp1, exp2):
        return self.find(exp1, exp2)


class InferenceEngine:
    def __init__(self):
        self.rules = []
        self.expressions = []
        self.applied_rule = None      

    def add_rule(self, rule: InferenceRule) -> None:
        self.rules.append(rule)

    def add_expression(self, exp: Expression) -> None:
        self.expressions.append(exp)

    def apply_rules(self) -> Expression:
        self.applied_rule = None
        if len(self.expressions) < 2:
            return None
        exp1, exp2 = self.expressions[0], self.expressions[1]
        for rule in self.rules:
            if rule.matches(exp1, exp2):
                self.applied_rule = rule
                return rule.apply(exp1, exp2)
        return None


def infer(expr1: str, expr2: str) -> str:
    
    engine = InferenceEngine()
    engine.add_rule(ModusPonens())
    engine.add_rule(ModusTollens())
    engine.add_rule(HypotheticalSyllogism())
    engine.add_rule(DisjunctiveSyllogism())
    engine.add_rule(Resolution())
    engine.add_expression(Expression(expr1))
    engine.add_expression(Expression(expr2))

    result = engine.apply_rules()
    if result is None:
        return "The input expression cannot be inferred"
    rule_name = type(engine.applied_rule).__name__
    return result.get_representation() + " (" + rule_name + ")"


def ask_bool(name: str) -> bool:
    while True:
        answer = input(name + " = ").strip().lower()
        if answer in ("true", "t", "1"):
            return True
        if answer in ("false", "f", "0"):
            return False
        print("Please type true or false")


def run_part1():
    solver = LogicalExpressionSolver()
    expression = Expression(input("Expression: "))
    try:
        variables = solver.get_variables(expression)   
        values = {}
        for var in variables:
            values[var] = ask_bool(var)
        result = solver.evaluate_expression(expression, values)
        print("true" if result else "false")
    except ValueError:
        print("Wrong expression")


def run_part2():
    expr1 = input("First expression: ")
    expr2 = input("Second expression: ")
    print(infer(expr1, expr2))


def main():
    while True:
        print()
        print("1) Evaluate a logical expression")
        print("2) Apply inference rules")
        print("0) Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            run_part1()
        elif choice == "2":
            run_part2()
        elif choice == "0":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()