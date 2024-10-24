from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
import json
from typing import Dict, Any
import os
import re

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS for frontend requests

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Update with your MySQL password
    database="rule_engine"
)
cursor = db.cursor(dictionary=True)

# Attribute catalog and user-defined functions
ATTRIBUTE_CATALOG = {"age", "department", "salary", "experience"}
USER_FUNCTIONS = {
    "isSenior": lambda age: int(age) > 60  # Example user-defined function
}

class Node:
    """Represents a node in the AST."""
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type
        self.left = left
        self.right = right
        self.value = value

    def to_dict(self):
        """Convert the node to a dictionary."""
        return {
            "type": self.type,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "value": self.value
        }

    @staticmethod
    def from_dict(data):
        """Recreate a node from a dictionary."""
        if not data:
            return None
        return Node(
            data["type"],
            Node.from_dict(data.get("left")),
            Node.from_dict(data.get("right")),
            data.get("value")
        )

@app.route("/")
def index():
    """Serve the HTML UI."""
    return render_template("index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files."""
    return send_from_directory(app.static_folder, filename)

def tokenize_rule(rule_string: str):
    """Split the rule string into tokens."""
    return re.findall(r"\(|\)|\w+\(\w+\)|\w+\s*[><=]\s*'?\w+'?|AND|OR", rule_string)

def parse_rule(rule_string: str) -> Node:
    """Parse the rule string into an AST with error handling."""
    if not rule_string or not isinstance(rule_string, str):
        raise ValueError("Invalid rule: Rule string must be a non-empty string.")

    # Tokenize the rule string
    tokens = tokenize_rule(rule_string)
    if not tokens:
        raise ValueError("Invalid rule: No valid tokens found.")

    output_stack = []  # Holds operands (AST nodes)
    operator_stack = []  # Holds operators and parentheses
    precedence = {"OR": 1, "AND": 2}  # Define operator precedence

    def pop_operator():
        """Pop an operator and build an AST node."""
        if len(output_stack) < 2:
            raise ValueError("Invalid rule: Missing operands for operator.")
        operator = operator_stack.pop()
        right = output_stack.pop()
        left = output_stack.pop()
        output_stack.append(Node("operator", left, right, operator))

    # Iterate over each token
    for token in tokens:
        # Handle user-defined functions like isSenior(age)
        if re.match(r"\w+\(\w+\)", token):  # Function like isSenior(age)
            output_stack.append(Node("operand", value=token.strip()))
        elif token in precedence:  # Handle AND / OR operators
            while operator_stack and operator_stack[-1] in precedence and \
                    precedence[operator_stack[-1]] >= precedence[token]:
                pop_operator()
            operator_stack.append(token)
        elif token == "(":  # Handle opening parenthesis
            operator_stack.append(token)
        elif token == ")":  # Handle closing parenthesis
            while operator_stack and operator_stack[-1] != "(":
                pop_operator()
            if not operator_stack or operator_stack[-1] != "(":
                raise ValueError("Mismatched parentheses in rule.")
            operator_stack.pop()  # Pop the "("
        else:  # Handle standard operands (e.g., age > 30)
            if not re.match(r"\w+\s*[><=]\s*'?\w+'?", token):
                raise ValueError(f"Invalid operand: {token}")
            output_stack.append(Node("operand", value=token.strip()))

    # Pop any remaining operators from the stack
    while operator_stack:
        pop_operator()

    # Ensure exactly one element remains in the output stack (the root node)
    if len(output_stack) != 1:
        raise ValueError("Invalid rule: Could not build a valid AST.")

    return output_stack[0]


def validate_attributes(data: Dict[str, Any]):
    """Validate data attributes against the catalog."""
    for key in data:
        if key not in ATTRIBUTE_CATALOG:
            raise ValueError(f"Invalid attribute: {key}")

def evaluate_node(node: Node, data: Dict[str, Any]) -> bool:
    """Evaluates an AST node against the input data."""
    if node.type == "operand":
        # Check if the operand is a user-defined function like isSenior(age)
        match = re.match(r"(\w+)\((\w+)\)", node.value)
        if match:
            func_name, arg = match.groups()
            if func_name in USER_FUNCTIONS:
                return USER_FUNCTIONS[func_name](data.get(arg))
            else:
                raise ValueError(f"Unknown function: {func_name}")

        # Handle standard attribute comparisons (e.g., age > 30)
        key, operator, value = re.split(r'\s*([><=])\s*', node.value)
        value = int(value) if value.isdigit() else value.strip("'")

        if operator == ">":
            return data.get(key, 0) > value
        elif operator == "<":
            return data.get(key, 0) < value
        elif operator == "=":
            return data.get(key, "") == value
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    elif node.type == "operator":
        left_result = evaluate_node(node.left, data) if node.left else False
        right_result = evaluate_node(node.right, data) if node.right else False

        if node.value == "AND":
            return left_result and right_result
        elif node.value == "OR":
            return left_result or right_result

    return False

@app.route("/api/create_rule", methods=["POST"])
def create_rule():
    """Create a rule with metadata and store it in the database."""
    try:
        rule_name = request.json.get("rule_name", "Unnamed Rule")
        description = request.json.get("description", "")
        rule_string = request.json.get("rule_string")
        status = request.json.get("status", "active")

        ast = parse_rule(rule_string)
        ast_json = json.dumps(ast.to_dict())

        query = """
            INSERT INTO rules (rule_name, description, rule_string, ast, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (rule_name, description, rule_string, ast_json, status))
        db.commit()

        return jsonify({"message": "Rule created successfully!", "ast": ast.to_dict()}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/evaluate_rule", methods=["POST"])
def evaluate_rule():
    """Evaluate the latest active rule."""
    try:
        data = request.json.get("data")
        validate_attributes(data)

        query = "SELECT ast FROM rules WHERE status = 'active' ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "No active rule found"}), 404

        ast = Node.from_dict(json.loads(result["ast"]))
        evaluation_result = evaluate_node(ast, data)
        return jsonify({"result": evaluation_result}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)