"""
Safe mathematical expression evaluation.

Evaluates mathematical expressions safely without using eval().
Supports basic arithmetic, common math functions, and constants.
"""

from typing import Dict, Any
import math
import operator
from ast import literal_eval, Expression, BinOp, UnaryOp, Name, Call, Constant
import ast

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


# Safe math functions that can be used in expressions
_SAFE_FUNCTIONS = {
    # Basic math
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "trunc": math.trunc,
    # Powers and roots
    "pow": pow,
    "power": pow,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    # Trigonometry
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    # Other
    "degrees": math.degrees,
    "radians": math.radians,
    "hypot": math.hypot,
    # Statistics (for lists)
    "sum": sum,
    "min": min,
    "max": max,
    "mean": lambda x: sum(x) / len(x) if len(x) > 0 else 0,
    "median": lambda x: (sorted(x)[len(x) // 2] if len(x) % 2 == 1 else (sorted(x)[len(x) // 2 - 1] + sorted(x)[len(x) // 2]) / 2) if len(x) > 0 else 0,
    "std": lambda x: (sum((xi - sum(x) / len(x)) ** 2 for xi in x) / len(x)) ** 0.5 if len(x) > 0 else 0,
    "std_dev": lambda x: (sum((xi - sum(x) / len(x)) ** 2 for xi in x) / len(x)) ** 0.5 if len(x) > 0 else 0,
    "variance": lambda x: sum((xi - sum(x) / len(x)) ** 2 for xi in x) / len(x) if len(x) > 0 else 0,
}

# Safe math constants
_SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "nan": math.nan,
}

# Safe operators
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class SafeEvaluator(ast.NodeVisitor):
    """Safe AST evaluator for mathematical expressions."""

    def visit(self, node):
        """Visit a node and return its value."""
        return super().visit(node)

    def visit_Constant(self, node):
        """Visit a constant (number, string, etc.)."""
        return node.value
    
    def visit_List(self, node):
        """Visit a list literal."""
        return [self.visit(item) for item in node.elts]
    
    def visit_Tuple(self, node):
        """Visit a tuple literal."""
        return tuple(self.visit(item) for item in node.elts)

    def visit_Name(self, node):
        """Visit a name (variable, function, constant)."""
        name = node.id
        if name in _SAFE_CONSTANTS:
            return _SAFE_CONSTANTS[name]
        raise ValueError(f"Unknown name: {name}")

    def visit_BinOp(self, node):
        """Visit a binary operation."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operation: {type(node.op)}")
        return op(left, right)

    def visit_UnaryOp(self, node):
        """Visit a unary operation."""
        operand = self.visit(node.operand)
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operation: {type(node.op)}")
        return op(operand)

    def visit_Call(self, node):
        """Visit a function call."""
        if not isinstance(node.func, Name):
            raise ValueError("Only simple function calls are supported")
        
        func_name = node.func.id
        if func_name not in _SAFE_FUNCTIONS:
            raise ValueError(f"Unknown function: {func_name}")
        
        func = _SAFE_FUNCTIONS[func_name]
        args = [self.visit(arg) for arg in node.args]
        
        # Handle special cases for statistical functions that work on lists
        if func_name in ("mean", "median", "std", "std_dev", "variance") and len(args) == 1:
            # These functions expect a list/tuple
            if isinstance(args[0], (list, tuple)):
                return func(args[0])
        
        return func(*args)


def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Supports:
    - Basic arithmetic: +, -, *, /, //, %, **
    - Math functions: sqrt, sin, cos, log, exp, etc.
    - Constants: pi, e, tau, inf, nan
    - Function calls: sqrt(16), sin(pi/2), mean([1,2,3])
    
    Args:
        expression: Mathematical expression as a string.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if evaluation succeeded.
            - result: The calculated result if successful, None otherwise.
            - error: Error message if evaluation failed, None if successful.
    
    Examples:
        >>> calculate("2 + 3")
        {"success": True, "result": 5, "error": None}
        
        >>> calculate("sqrt(16)")
        {"success": True, "result": 4.0, "error": None}
        
        >>> calculate("sin(pi/2)")
        {"success": True, "result": 1.0, "error": None}
        
        >>> calculate("mean([1,2,3,4,5])")
        {"success": True, "result": 3.0, "error": None}
    """
    try:
        if not expression or not expression.strip():
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "Expression cannot be empty",
            }
        
        # Parse the expression into an AST
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid expression syntax: {str(e)}",
            }
        
        # Evaluate the AST safely
        evaluator = SafeEvaluator()
        result = evaluator.visit(tree.body)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: result,
            ERROR_KEY: None,
        }
    
    except ValueError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Evaluation error: {str(e)}",
        }
    except ZeroDivisionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Division by zero: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Unexpected error: {str(e)}",
        }

