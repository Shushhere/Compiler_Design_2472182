# SLR(1) Parser
# Grammar:
# S -> C C
# C -> c C | d

from collections import defaultdict

grammar = {
    "S": [["C", "C"]],
    "C": [["c", "C"], ["d"]]
}

start_symbol = "S"
augmented_start = "S'"

non_terminals = set(grammar.keys())
terminals = {"c", "d", "$"}

productions = [(augmented_start, [start_symbol])]
for lhs in grammar:
    for rhs in grammar[lhs]:
        productions.append((lhs, rhs))

# FIRST sets
FIRST = {
    "S": {"c", "d"},
    "C": {"c", "d"}
}

# FOLLOW sets
FOLLOW = {
    "S": {"$"},
    "C": {"c", "d", "$"}
}

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

    return closure(moved) if moved else frozenset()

# Canonical LR(0) collection
states = []
transitions = {}

initial = closure({(augmented_start, (start_symbol,), 0)})
states.append(initial)

i = 0
while i < len(states):
    state = states[i]

    for symbol in terminals | non_terminals:
        next_state = goto(state, symbol)

        if next_state:
            if next_state not in states:
                states.append(next_state)

            j = states.index(next_state)
            transitions[(i, symbol)] = j

    i += 1

# Display LR(0) item sets
print("\nCANONICAL LR(0) ITEM SETS")
print("=" * 50)

for i, state in enumerate(states):
    print(f"\nI{i}:")
    for lhs, rhs, dot in sorted(state):
        rhs_list = list(rhs)
        rhs_list.insert(dot, "•")
        print(f"  {lhs} -> {' '.join(rhs_list)}")

# Build SLR ACTION and GOTO tables
ACTION = defaultdict(dict)
GOTO = defaultdict(dict)

for i, state in enumerate(states):
    for lhs, rhs, dot in state:

        # Shift action
        if dot < len(rhs):
            symbol = rhs[dot]

            if symbol in terminals - {"$"}:
                j = transitions[(i, symbol)]
                ACTION[i][symbol] = f"S{j}"

            elif symbol in non_terminals:
                j = transitions[(i, symbol)]
                GOTO[i][symbol] = j

        # Reduce or accept action
        else:
            if lhs == augmented_start:
                ACTION[i]["$"] = "ACCEPT"
            else:
                production_number = productions.index((lhs, list(rhs)))

                # Reduction only on FOLLOW(lhs)
                for terminal in FOLLOW[lhs]:
                    ACTION[i][terminal] = f"R{production_number}"

# Display production list
print("\nPRODUCTIONS")
print("-" * 40)

for i, (lhs, rhs) in enumerate(productions):
    print(f"R{i}: {lhs} -> {' '.join(rhs)}")

# Display FOLLOW sets
print("\nFOLLOW SETS")
print("-" * 40)

for symbol, values in FOLLOW.items():
    print(f"FOLLOW({symbol}) = {{ {', '.join(sorted(values))} }}")

# Display ACTION table
print("\nSLR ACTION TABLE")
print("-" * 40)

for state in range(len(states)):
    for terminal, action in ACTION[state].items():
        print(f"ACTION[{state}, {terminal}] = {action}")

# Display GOTO table
print("\nSLR GOTO TABLE")
print("-" * 40)

for state in range(len(states)):
    for symbol, next_state in GOTO[state].items():
        print(f"GOTO[{state}, {symbol}] = {next_state}")

# Parsing function
def parse(input_string):
    tokens = list(input_string.strip()) + ["$"]
    stack = [0]
    index = 0
    step = 1

    print("\nSLR(1) PARSING PROCESS")
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

            # Pop two stack entries per grammar symbol
            for _ in range(2 * len(rhs)):
                stack.pop()

            state = stack[-1]
            next_state = GOTO[state][lhs]

            stack.append(lhs)
            stack.append(next_state)

            description = f"Reduce {lhs} -> {' '.join(rhs)}, goto {next_state}"

        print(f"{step:<6}{stack_display:<25}{input_display:<20}{description}")
        step += 1


# Main
print("\nSLR(1) PARSER")
print("Grammar: S -> C C, C -> c C | d")

user_input = input("\nEnter input string (c and d only): ")

if all(ch in "cd" for ch in user_input) and user_input:
    if parse(user_input):
        print("\nResult: String ACCEPTED.")
    else:
        print("\nResult: String REJECTED.")
else:
    print("\nInvalid input. Enter a non-empty string using c and d only.")
