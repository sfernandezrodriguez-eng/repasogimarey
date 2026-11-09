import ast
import math
import tkinter as tk


BACKGROUND = "#1C1C1E"
DISPLAY_BACKGROUND = "#2C2C2E"
BUTTON_BACKGROUND = "#3A3A3C"
ORANGE = "#FF9500"
MAX_EXPRESSION_LENGTH = 200


def safe_evaluate(expression):
    """Evaluate only the arithmetic operations supported by the calculator."""
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numeric values are allowed")
            return node.value
        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow) and right == 2:
                return left ** 2
            raise ValueError("Unsupported operation")
        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value
            raise ValueError("Unsupported operation")
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "sqrt"
            and len(node.args) == 1
            and not node.keywords
        ):
            return math.sqrt(evaluate(node.args[0]))
        raise ValueError("Invalid expression")

    result = evaluate(tree)
    if isinstance(result, float) and not math.isfinite(result):
        raise OverflowError("Result is not finite")
    return result


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora")
        self.root.configure(bg=BACKGROUND)
        self.root.minsize(320, 420)
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.just_calculated = False

        display = tk.Entry(
            root,
            textvariable=self.expression,
            state="readonly",
            readonlybackground=DISPLAY_BACKGROUND,
            disabledforeground="#FFFFFF",
            foreground="#FFFFFF",
            insertbackground="#FFFFFF",
            font=("Arial", 20),
            justify="right",
            relief="flat",
            bd=0,
        )
        display.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=12, pady=(14, 4), ipady=12)

        result_label = tk.Label(
            root,
            textvariable=self.result,
            bg=BACKGROUND,
            fg="#FFFFFF",
            font=("Arial", 30),
            anchor="e",
            padx=12,
        )
        result_label.grid(row=1, column=0, columnspan=6, sticky="nsew", pady=(0, 12))

        buttons = [
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("/", 2, 3), ("(", 2, 4), (")", 2, 5),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("*", 3, 3), ("√x", 3, 4), ("x²", 3, 5),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("-", 4, 3), ("C", 4, 4), ("⌫", 4, 5),
            ("0", 5, 0, 2), (".", 5, 2), ("+", 5, 3), ("=", 5, 4, 2),
        ]

        for item in buttons:
            label, row, column, *span = item
            columnspan = span[0] if span else 1
            color = ORANGE if label == "=" else "#32CD32" if label == "0" else BUTTON_BACKGROUND
            button = tk.Button(
                root,
                text=label,
                command=lambda value=label: self.press(value),
                bg=color,
                fg="#FFFFFF",
                activebackground=(
                    "#CC7A00" if label == "=" else "#228B22" if label == "0" else "#545456"
                ),
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                font=("Arial", 18, "bold"),
                takefocus=False,
            )
            button.grid(
                row=row,
                column=column,
                columnspan=columnspan,
                sticky="nsew",
                padx=5,
                pady=5,
                ipadx=4,
                ipady=10,
            )

        for row in range(2, 6):
            root.rowconfigure(row, weight=1, minsize=52)
        for column in range(6):
            root.columnconfigure(column, weight=1, minsize=42)
        root.rowconfigure(0, weight=0)
        root.rowconfigure(1, weight=0)

        root.bind_all("<Key>", self.handle_key)

    def press(self, key):
        if key == "C":
            self.clear()
        elif key == "⌫":
            self.backspace()
        elif key == "=":
            self.calculate()
        elif key == "√x":
            self.append("sqrt(")
        elif key == "x²":
            self.append("**2")
        else:
            self.append(key)

    def append(self, text):
        current = self.expression.get()
        if self.just_calculated:
            if text in "0123456789.(" or text == "sqrt(":
                current = ""
            elif self.result.get() != "Error":
                current = self.result.get()
            self.just_calculated = False
        self.expression.set(current + text)
        self.result.set("0")

    def clear(self):
        self.expression.set("")
        self.result.set("0")
        self.just_calculated = False

    def backspace(self):
        self.expression.set(self.expression.get()[:-1])
        self.result.set("0")
        self.just_calculated = False

    def calculate(self):
        expression = self.expression.get()
        if not expression:
            return
        try:
            value = safe_evaluate(expression)
            if isinstance(value, float):
                displayed = format(value, ".12g")
            else:
                displayed = str(value)
            self.result.set(displayed)
        except (ArithmeticError, SyntaxError, ValueError, TypeError):
            self.result.set("Error")
        self.just_calculated = True

    def handle_key(self, event):
        if event.keysym in ("Return", "KP_Enter"):
            self.calculate()
            return "break"
        if event.keysym == "BackSpace":
            self.backspace()
            return "break"
        if event.keysym == "Escape":
            self.clear()
            return "break"
        if event.char and event.char in "0123456789.+-*/()":
            self.append(event.char)
            return "break"
        return None


def main():
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
