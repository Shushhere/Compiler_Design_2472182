# Canonical LR(1) (CLR(1)) Parser
# Grammar:
# E -> E + T | T
# T -> T * F | F
# F -> ( E ) | id

from collections import defaultdict
import re

# ---------------- GRAMMAR ----------------

grammar = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["(", "E", ")"], ["id"]]
}

start_symbol = "E"
augmented_start = "E'"

# Production list
productions = [(augmented_start, [start_symbol])]

for lhs in grammar:
    for rhs in grammar[lhs]:
        productions.append((lhs, rhs))

non_terminals = set(grammar.keys()) | {augmented_start}

terminals = set()
for lhs, rhs in productions:
    for symbol in rhs:
        if symbol not in non_terminals:
            terminals.add(symbol)

terminals.add("$")

# ---------------- FIRST SETS ----------------

FIRST = {nt: set() for nt in non_terminals}

def compute_first():
    changed = True

    while changed:
        changed = False

        for lhs, rhs in productions:
            for symbol in rhs:

                if symbol in terminals:
                    if symbol not in FIRST[lhs]:
                        FIRST[lhs].add(symbol)
                        changed = True
                    break

                old_size = len(FIRST[lhs])
                FIRST[lhs].update(FIRST[symbol])
                if len(FIRST[lhs]) != old_size:
                    changed = True

                # This grammar has no epsilon productions
                break

compute_first()

def first_sequence(sequence):
    result = set()

    for symbol in sequence:
        if symbol in terminals:
            result.add(symbol)
            return result

        result.update(FIRST[symbol])
        return result

    return result

# ---------------- CLR(1) CLOSURE ----------------

def closure(items):
    result = set(items)
    changed = True

    while changed:
        changed = False
        additions = set()

        for lhs, rhs, dot, lookahead in result:

            if dot < len(rhs):
                symbol = rhs[dot]

                if symbol in non_terminals:
                    beta = rhs[dot + 1:]
                    lookaheads = first_sequence(beta + (lookahead,))

                    for production_lhs, production_rhs in productions:
                        if production_lhs == symbol:

                            for la in lookaheads:
                                item = (
                                    production_l0 if False else production_lhs,
                                    tuple(production_rhs),
                                    0,
                                    la
                                )

                                if item not in result:
                                    additions.add(item)

        if additions:
            result.update(additions)
            changed = True

    return frozenset(result)

# ---------------- GOTO FUNCTION ----------------

def goto(items, symbol):
    moved = set()

    for lhs, rhs, dot, lookahead in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1, lookahead))

    if moved:
        return closure(moved)

    return frozenset()

# ---------------- CANONICAL COLLECTION ----------------

initial_item = (augmented_start, (start_symbol,), 0, "$")
states = [closure({initial_item})]
transitions = {}

i = 0
all_symbols = terminals | non_terminals

while i < len(states):
    state = states[i]

    for symbol in all_symbols:
        next_state = goto(state, symbol)

        if next_state:
            if next_state not in states:
                states.append(next_state)

            j = states.index(next_state)
            transitions[(i, symbol)] = j

    i += 1

# ---------------- DISPLAY ITEM SETS ----------------

print("\nCANONICAL LR(1) ITEM SETS")
print("=" * 60)

for i, state in enumerate(states):
    print(f"\nI{i}:")

    for lhs, rhs, dot, lookahead in sorted(state):
        rhs_symbols = list(rhs)
        rhs_symbols.insert(dot, "•")

        print(f"  {lhs} -> {' '.join(rhs_symbols)}, {lookahead}")

# ---------------- BUILD ACTION AND GOTO ----------------

ACTION = defaultdict(dict)
GOTO = defaultdict(dict)
conflicts = []

def add_action(state, terminal, action):
    if terminal in ACTION[state] and ACTION[state][terminal] != action:
        conflicts.append(
            (state, terminal, ACTION[state][terminal], action)
        )
    else:
        ACTION[state][terminal] = action

for i, state in enumerate(states):

    for lhs, rhs, dot, lookahead in state:

        # SHIFT
        if dot < len(rhs):
            symbol = rhs[dot]

            if symbol in terminals - {"$"}:
                j = transitions[(i, symbol)]
                add_action(i, symbol, f"S{j}")

            elif symbol in non_terminals:
                GOTO[i][symbol] = transitions[(i, symbol)]

        # REDUCE / ACCEPT
        else:
            if lhs == augmented_start:
                add_action(i, "$", "ACCEPT")
            else:
                production_number = productions.index((lhs, list(rhs)))
                add_action(i, lookahead, f"R{production_number}")

# ---------------- DISPLAY PRODUCTIONS ----------------

print("\nPRODUCTION RULES")
print("-" * 40)

for i, (lhs, rhs) in enumerate(productions):
    print(f"R{i}: {lhs} -> {' '.join(rhs)}")

# ---------------- DISPLAY FIRST ----------------

print("\nFIRST SETS")
print("-" * 40)

for nt in grammar:
    print(f"FIRST({nt}) = {{ {', '.join(sorted(FIRST[nt]))} }}")

# ---------------- DISPLAY ACTION TABLE ----------------

print("\nCLR(1) ACTION TABLE")
print("-" * 40)

for state in range(len(states)):
    for terminal in sorted(terminals):
        if terminal in ACTION[state]:
            print(f"ACTION[{state}, {terminal}] = {ACTION[state][terminal]}")

# ---------------- DISPLAY GOTO TABLE ----------------

print("\nCLR(1) GOTO TABLE")
print("-" * 40)

for state in range(len(states)):
    for nt in sorted(non_terminals - {augmented_start}):
        if nt in GOTO[state]:
            print(f"GOTO[{state}, {nt}] = {GOTO[state][nt]}")

# ---------------- TOKENIZER ----------------

def tokenize(expression):
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[()+*]", expression)

    # Convert identifiers into id
    tokens = [
        "id" if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token)
        else token
        for token in tokens
    ]

    # Validate that no invalid characters were ignored
    reconstructed = "".join(tokens)
    original = re.sub(r"\s+", "", expression)

    if reconstructed != original:
        raise ValueError("Invalid characters in expression.")

    return tokens + ["$"]

# ---------------- PARSING ----------------

def parse(expression):
    tokens = tokenize(expression)

    stack = [0]
    index = 0
    step = 1

    print("\nCLR(1) PARSING PROCESS")
    print("=" * 100)
    print(f"{'Step':<6}{'Stack':<35}{'Input':<30}{'Action'}")
    print("-" * 100)

    while True:
        state = stack[-1]
        current = tokens[index]

        stack_display = " ".join(map(str, stack))
        input_display = " ".join(tokens[index:])

        action = ACTION[state].get(current)

        if action is None:
            print(f"{step:<6}{stack_display:<35}{input_display:<30}ERROR")
            return False

        if action == "ACCEPT":
            print(f"{step:<6}{stack_display:<35}{input_display:<30}ACCEPT")
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

            for _ in range(2 * len(rhs)):
                stack.pop()

            state = stack[-1]
            next_state = GOTO[state][lhs]

            stack.append(lhs)
            stack.append(next_state)

            description = f"Reduce {lhs} -> {' '.join(rhs)}, goto {next_state}"

        print(f"{step:<6}{stack_display:<35}{input_display:<30}{description}")
        step += 1

# ---------------- MAIN ----------------

print("\nCANONICAL LR(1) PARSER")
print("Grammar: E -> E + T | T")
print("        T -> T * F | F")
print("        F -> ( E ) | id")

if conflicts:
    print("\nParsing table contains conflicts:")
    for conflict in conflicts:
        print(conflict)
else:
    print("\nGrammar is CLR(1): No parsing table conflicts.")

expression = input("\nEnter expression: ")

try:
    if parse(expression):
        print("\nResult: Expression ACCEPTED.")
    else:
        print("\nResult: Expression REJECTED.")
except (ValueError, IndexError, KeyError):
    print("\nResult: Expression REJECTED.")
