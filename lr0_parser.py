# LR(0) Parser
# Grammar:
# S -> C C
# C -> c C
# C -> d

from collections import defaultdict

# Grammar productions
grammar = {
    "S": [["C", "C"]],
    "C": [["c", "C"], ["d"]]
}

start_symbol = "S"
augmented_start = "S'"

# Augmented grammar
grammar[augmented_start] = [[start_symbol]]

non_terminals = set(grammar.keys())
terminals = {"c", "d", "$"}

# Create production list
productions = []
for lhs in grammar:
    for rhs in grammar[lhs]:
        productions.append((lhs, rhs))

# Add augmented production
productions.insert(0, (augmented_start, [start_symbol]))

def closure(items):
    result = set(items)
    changed = True

    while changed:
        changed = False
        new_items = set()

        for lhs, rhs, dot in result:
            if dot < len(rhs):
                symbol = rhs[dot]

                if symbol in non_terminals:
                    for production in grammar[symbol]:
                        item = (symbol, tuple(production), 0)
                        if item not in result:
                            new_items.add(item)

        if new_items:
            result.update(new_items)
            changed = True

    return frozenset(result)

def goto(items, symbol):
    moved = set()

    for lhs, rhs, dot in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1))

    if moved:
        return closure(moved)

    return frozenset()

# Build canonical collection of LR(0) items
C = []
transitions = {}
initial_state = closure({(augmented_start, (start_symbol,), 0)})
C.append(initial_state)

i = 0
while i < len(C):
    state = C[i]

    for symbol in terminals | non_terminals:
        next_state = goto(state, symbol)

        if next_state:
            if next_state not in C:
                C.append(next_state)

            j = C.index(next_state)
            transitions[(i, symbol)] = j

    i += 1

# Display item sets
print("\nCANONICAL LR(0) ITEM SETS")
print("=" * 50)

for i, state in enumerate(C):
    print(f"\nI{i}:")
    for lhs, rhs, dot in sorted(state):
        rhs_symbols = list(rhs)
        rhs_symbols.insert(dot, "•")
        print(f"   {lhs} -> {' '.join(rhs_symbols)}")

# Build LR(0) parsing table
ACTION = defaultdict(dict)
GOTO = defaultdict(dict)

for i, state in enumerate(C):
    for lhs, rhs, dot in state:

        # Shift
        if dot < len(rhs):
            symbol = rhs[dot]

            if symbol in terminals - {"$"}:
                j = transitions[(i, symbol)]
                ACTION[i][symbol] = f"S{j}"

            elif symbol in non_terminals:
                j = transitions[(i, symbol)]
                GOTO[i][symbol] = j

        # Reduce or Accept
        else:
            if lhs == augmented_start:
                ACTION[i]["$"] = "ACCEPT"
            else:
                production_number = productions.index((lhs, list(rhs)))
                for terminal in terminals:
                    ACTION[i][terminal] = f"R{production_number}"

# Display parsing table
print("\n\nLR(0) PARSING TABLE")
print("=" * 50)

print("Productions:")
for i, (lhs, rhs) in enumerate(productions):
    print(f"R{i}: {lhs} -> {' '.join(rhs)}")

print("\nACTION TABLE")
print("-" * 40)
for state in range(len(C)):
    for terminal, action in ACTION[state].items():
        print(f"ACTION[{state}, {terminal}] = {action}")

print("\nGOTO TABLE")
print("-" * 40)
for state in range(len(C)):
    for non_terminal, next_state in GOTO[state].items():
        print(f"GOTO[{state}, {non_terminal}] = {next_state}")

# Parse input
def parse(input_string):
    tokens = list(input_string.strip()) + ["$"]
    stack = [0]
    index = 0
    step = 1

    print("\n\nLR(0) PARSING PROCESS")
    print("=" * 85)
    print(f"{'Step':<6}{'Stack':<25}{'Input':<20}{'Action'}")
    print("-" * 85)

    while True:
        state = stack[-1]
        current = tokens[index]
        stack_display = " ".join(map(str, stack))
        input_display = " ".join(tokens[index:])

        action = ACTION[state].get(current)

        if action is None:
            print(f"{step:<6}{stack_display:<25}{input_display:<20}ERROR")
            return False

        if action == "ACCEPT":
            print(f"{step:<6}{stack_display:<25}{input_display:<20}ACCEPT")
            return True

        elif action.startswith("S"):
            next_state = int(action[1:])
            stack.append(current)
            stack.append(next_state)
            index += 1
            description = f"Shift {current}, goto {next_state}"

        elif action.startswith("R"):
            production_number = int(action[1:])
            lhs, rhs = productions[production_number]

            # Pop 2 entries per grammar symbol
            for _ in range(len(rhs) * 2):
                stack.pop()

            state = stack[-1]
            next_state = GOTO[state][lhs]

            stack.append(lhs)
            stack.append(next_state)

            description = f"Reduce {lhs} -> {' '.join(rhs)}, goto {next_state}"

        print(f"{step:<6}{stack_display:<25}{input_display:<20}{description}")
        step += 1


# Main
print("\nLR(0) PARSER")
print("Grammar: S -> C C, C -> c C | d")
user_input = input("\nEnter input string (c and d only): ")

if all(ch in "cd" for ch in user_input):
    if parse(user_input):
        print("\nResult: String ACCEPTED.")
    else:
        print("\nResult: String REJECTED.")
else:
    print("\nInvalid input. Only c and d are allowed.")
