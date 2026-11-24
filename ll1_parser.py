# LL(1) Predictive Parser

# Grammar:
# E  -> T E'
# E' -> + T E' | epsilon
# T  -> F T'
# T' -> * F T' | epsilon
# F  -> ( E ) | id

productions = {
    "E":  [["T", "E'"]],
    "E'": [["+", "T", "E'"], ["ε"]],
    "T":  [["F", "T'"]],
    "T'": [["*", "F", "T'"], ["ε"]],
    "F":  [["(", "E", ")"], ["id"]]
}

# FIRST sets
FIRST = {
    "E":  {"(", "id"},
    "E'": {"+", "ε"},
    "T":  {"(", "id"},
    "T'": {"*", "ε"},
    "F":  {"(", "id"}
}

# FOLLOW sets
FOLLOW = {
    "E":  {")", "$"},
    "E'": {")", "$"},
    "T":  {"+", ")", "$"},
    "T'": {"+", ")", "$"},
    "F":  {"*", "+", ")", "$"}
}

# Predictive parsing table
table = {
    "E":  {"id": "T E'", "(": "T E'"},
    "E'": {"+": "+ T E'", ")": "ε", "$": "ε"},
    "T":  {"id": "F T'", "(": "F T'"},
    "T'": {"*": "* F T'", "+": "ε", ")": "ε", "$": "ε"},
    "F":  {"(": "( E )", "id": "id"}
}

def display_sets(title, sets):
    print("\n" + title)
    print("-" * 35)
    for symbol, values in sets.items():
        print(f"{symbol:<5} = {{ {', '.join(sorted(values))} }}")

def parse_string(input_string):
    tokens = input_string.strip().split()
    tokens.append("$")

    stack = ["$", "E"]
    index = 0
    step = 1

    print("\nPARSING PROCESS")
    print("-" * 75)
    print(f"{'Step':<6}{'Stack':<25}{'Input':<25}{'Action'}")
    print("-" * 75)

    while stack:
        top = stack[-1]
        current = tokens[index]

        stack_display = " ".join(stack)
        input_display = " ".join(tokens[index:])

        if top == current == "$":
            print(f"{step:<6}{stack_display:<25}{input_display:<25} ACCEPT")
            return True

        # Terminal matching
        if top not in productions:
            if top == current:
                stack.pop()
                index += 1
                action = f"Match {current}"
            else:
                action = "ERROR: Terminal mismatch"
                print(f"{step:<6}{stack_display:<25}{input_display:<25}{action}")
                return False

        # Non-terminal expansion
        else:
            if current in table[top]:
                production = table[top][current]
                stack.pop()

                if production != "ε":
                    symbols = production.split()
                    stack.extend(reversed(symbols))

                action = f"{top} -> {production}"
            else:
                action = "ERROR: No production found"
                print(f"{step:<6}{stack_display:<25}{input_display:<25}{action}")
                return False

        print(f"{step:<6}{stack_display:<25}{input_display:<25}{action}")
        step += 1

    return False


# Main program
display_sets("FIRST SETS", FIRST)
display_sets("FOLLOW SETS", FOLLOW)

print("\nPREDICTIVE PARSING TABLE")
print("-" * 45)
for non_terminal, entries in table.items():
    for terminal, production in entries.items():
        print(f"M[{non_terminal}, {terminal}] = {non_terminal} -> {production}")

print("\nEnter expression tokens separated by spaces.")
print("Example: id + id * id")
user_input = input("Input: ")

if parse_string(user_input):
    print("\nResult: String ACCEPTED.")
else:
    print("\nResult: String REJECTED.")
