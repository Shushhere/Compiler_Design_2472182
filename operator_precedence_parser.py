# Operator Precedence Parser

# Precedence table
precedence = {
    '+': {'+': '>', '-': '>', '*': '<', '/': '<', 'id': '<', '(': '<', ')': '>', '$': '>'},
    '-': {'+': '>', '-': '>', '*': '<', '/': '<', 'id': '<', '(': '<', ')': '>', '$': '>'},
    '*': {'+': '>', '-': '>', '*': '>', '/': '>', 'id': '<', '(': '<', ')': '>', '$': '>'},
    '/': {'+': '>', '-': '>', '*': '>', '/': '>', 'id': '<', '(': '<', ')': '>', '$': '>'},
    'id': {'+': '>', '-': '>', '*': '>', '/': '>', ')': '>', '$': '>'},
    '(': {'+': '<', '-': '<', '*': '<', '/': '<', 'id': '<', '(': '<', ')': '=', '$': None},
    ')': {'+': '>', '-': '>', '*': '>', '/': '>', ')': '>', '$': '>'},
    '$': {'+': '<', '-': '<', '*': '<', '/': '<', 'id': '<', '(': '<', ')': None, '$': 'ACCEPT'}
}

operators = {'+', '-', '*', '/'}

def tokenize(expression):
    tokens = []
    i = 0

    while i < len(expression):
        if expression[i].isspace():
            i += 1
            continue

        if expression[i].isalpha() or expression[i] == '_':
            start = i
            while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                i += 1
            tokens.append('id')
            continue

        if expression[i].isdigit():
            start = i
            while i < len(expression) and expression[i].isdigit():
                i += 1
            tokens.append('id')
            continue

        if expression[i] in operators or expression[i] in '()':
            tokens.append(expression[i])
            i += 1
            continue

        raise ValueError(f"Invalid character: {expression[i]}")

    tokens.append('$')
    return tokens

def parse(expression):
    tokens = tokenize(expression)
    stack = ['$']
    index = 0
    step = 1

    print("\nOPERATOR PRECEDENCE PARSING")
    print("-" * 75)
    print(f"{'Step':<6}{'Stack':<25}{'Input':<25}{'Relation':<12}{'Action'}")
    print("-" * 75)

    while True:
        top = stack[-1]
        current = tokens[index]

        stack_str = " ".join(stack)
        input_str = " ".join(tokens[index:])

        if top == '$' and current == '$':
            print(f"{step:<6}{stack_str:<25}{input_str:<25}{'':<12}ACCEPT")
            return True

        # Shift if top is a terminal
        relation = precedence.get(top, {}).get(current)

        if relation == '<' or relation == '=':
            stack.append(current)
            index += 1
            action = f"Shift {current}"

        elif relation == '>':
            # Reduce
            if stack[-1] == 'id':
                stack.pop()
                stack.append('E')
                action = "Reduce: E -> id"

            elif stack[-1] == ')':
                if '(' in stack:
                    while stack[-1] != '(':
                        stack.pop()
                    stack.pop()
                    stack.append('E')
                    action = "Reduce: E -> ( E )"
                else:
                    print(f"{step:<6}{stack_str:<25}{input_str:<25}{'ERROR':<12}Unmatched )")
                    return False

            elif stack[-1] == 'E':
                # Find the rightmost operator
                if len(stack) >= 3 and stack[-2] in operators:
                    op = stack[-2]
                    stack.pop()       # Remove E
                    stack.pop()       # Remove operator
                    stack.pop()       # Remove E
                    stack.append('E')
                    action = f"Reduce: E -> E {op} E"
                else:
                    print(f"{step:<6}{stack_str:<25}{input_str:<25}{'ERROR':<12}Invalid reduction")
                    return False

            else:
                print(f"{step:<6}{stack_str:<25}{input_str:<25}{'ERROR':<12}No valid reduction")
                return False

        else:
            print(f"{step:<6}{stack_str:<25}{input_str:<25}{'ERROR':<12}No precedence relation")
            return False

        print(f"{step:<6}{stack_str:<25}{input_str:<25}{relation:<12}{action}")
        step += 1


# Main program
print("OPERATOR PRECEDENCE PARSER")
print("Supported operators: +, -, *, /, parentheses")
expression = input("Enter expression: ")

try:
    if parse(expression):
        print("\nResult: Expression ACCEPTED.")
    else:
        print("\nResult: Expression REJECTED.")
except ValueError as error:
    print("\nLexical Error:", error)
    print("Result: Expression REJECTED.")
