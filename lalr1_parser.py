# LALR(1) Parser
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

non_terminals = set(grammar) | {augmented_start}

productions = [(augmented_start, [start_symbol])]
for lhs in grammar:
    for rhs in grammar[lhs]:
        productions.append((lhs, rhs))

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
            symbol = rhs[0]

            if symbol in terminals:
                if symbol not in FIRST[lhs]:
                    FIRST[lhs].add(symbol)
                    changed = True
            else:
                old_size = len(FIRST[lhs])
                FIRST[lhs].update(FIRST[symbol])

                if len(FIRST[lhs]) != old_size:
                    changed = True

compute_first()

def first_sequence(sequence):
    if not sequence:
        return {"ε"}

    symbol = sequence[0]

    if symbol in terminals:
        return {symbol}

    return FIRST[symbol].copy()

# ---------------- LR(1) CLOSURE ----------------

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

                    for p_lhs, p_rhs in productions:
                        if p_lhs == symbol:
                            for la in lookaheads:
                                item = (p_lhs, tuple(p_rhs), 0, la)

                                if item not in result:
                                    additions.add(item)

        if additions:
            result.update(additions)
            changed = True

    return frozenset(result)

# ---------------- GOTO ----------------

def goto(items, symbol):
    moved = set()

    for lhs, rhs, dot, lookahead in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1, lookahead))

    return closure(moved) if moved else frozenset()

# ---------------- CLR(1) STATES ----------------

initial_item = (augmented_start, (start_symbol,), 0, "$")

clr_states = [closure({initial_item})]
clr_transitions = {}

i = 0
while i < len(clr_states):
    state = clr_states[i]

    for symbol in terminals | non_terminals:
        next_state = goto(state, symbol)

        if next_state:
            if next_state not in clr_states:
                clr_states.append(next_state)

            j = clr_states.index(next_state)
            clr_transitions[(i, symbol)] = j

    i += 1

# ---------------- MERGE LR(1) STATES ----------------

# LR(0) core = production and dot position,
# excluding lookahead symbols.

def core(state):
    return frozenset(
        (lhs, rhs, dot)
        for lhs, rhs, dot, lookahead in state
    )

lalr_states = []
core_to_state = {}
clr_to_lalr = {}

for i, state in enumerate(clr_states):
    state_core = core(state)

    if state_core not in core_to_state:
        new_id = len(lalr_states)
        core_to_state[state_core] = new_id
        lalr_states.append(set())

    new_id = core_to_state[state_core]
    lalr_states[new_id].update(state)
    clr_to_lalr[i] = new_id

lalr_states = [
    frozenset(state) for state in lalr_states
]

# Merge transitions
lalr_transitions = {}

for (i, symbol), j in clr_transitions.items():
    new_i = clr_to_lalr[i]
    new_j = clr_to_lalr[j]

    lalr_transitions[(new_i, symbol)] = new_j

# ---------------- DISPLAY CLR STATES ----------------

print("\nCANONICAL CLR(1) STATES BEFORE MERGING")
print("=" * 60)

for i, state in enumerate(clr_states):
    print(f"\nI{i}:")

    for lhs, rhs, dot, lookahead in sorted(state):
        rhs_symbols = list(rhs)
        rhs_symbols.insert(dot, "•")

        print(f"  {lhs} -> {' '..join(rhs_symbols)}, {lookahead}")

# ---------------- DISPLAY LALR STATES ----------------

print("\n\nLALR(1) STATES AFTER MERGING")
print("=" * 60)

for i, state in enumerate(lalr_states):
    print(f"\nI{i}:")

    for lhs, rhs, dot, lookahead in sorted(state):
        rhs_symbols = list(rhs)
        rhs_symbols.insert(dot, "•")

        print(f"  {lhs} -> {' '..join(rhs_symbols)}, {lookahead}")

print(f"\nCLR(1) states: {len(clr_states)}")
print(f"LALR(1) states: {len(lalr_states)}")

# ---------------- ACTION AND GOTO TABLES ----------------

ACTION = defaultdict(dict)
GOTO = defaultdict(dict)
conflicts = []

def add_action(state, terminal, action):
    if terminal in ACTION[state]:
        if ACTION[state][terminal] != action:
            conflicts.append(
                (state, terminal, ACTION[state][terminal], action)
            )
    else:
        ACTION[state][terminal] = action

for i, state in enumerate(lalr_states):

    for lhs, rhs, dot, lookahead in state:

        # SHIFT
        if dot < len(rhs):
            symbol = rhs[dot]

            if symbol in terminals - {"$"}:
                j = lalr_transitions[(i, symbol)]
                add_action(i, symbol, f"S{j}")

            elif symbol in non_terminals - {augmented_start}:
                GOTO[i][symbol] = lalr_transitions[(i, symbol)]

        # REDUCE / ACCEPT
        else:
            if lhs == augmented_start:
                add_action(i, "$", "ACCEPT")
            else:
                production_number = productions.index(
                    (lhs, list(rhs))
                )

                add_action(
                    i,
                    lookahead,
                    f"R{production_number}"
                )

# ---------------- DISPLAY PRODUCTIONS ----------------

print("\nPRODUCTION RULES")
print("-" * 45)

for i, (lhs, rhs) in enumerate(productions):
    print(f"R{i}: {lhs} -> {' '..join(rhs)}")

# ---------------- DISPLAY FIRST SETS ----------------

print("\nFIRST SETS")
print("-" * 45)

for nt in grammar:
    print(f"FIRST({nt}) = {{ {', '.join(sorted(FIRST[nt]))} }}")

# ---------------- DISPLAY ACTION TABLE ----------------

print("\nLALR(1) ACTION TABLE")
print("-" * 45)

for state in range(len(lalr_states)):
    for terminal in sorted(terminals):
        if terminal in ACTION[state]:
            print(
                f"ACTION[{state}, {terminal}] = "
                f"{ACTION[state][terminal]}"
            )

# ---------------- DISPLAY GOTO TABLE ----------------

print("\nLALR(1) GOTO TABLE")
print("-" * 45)

for state in range(len(lalr_states)):
    for nt in sorted(non_terminals - {augmented_start}):
        if nt in GOTO[state]:
            print(f"GOTO[{state}, {nt}] = {GOTO[state][nt]}")

# ---------------- TOKENIZER ----------------

def tokenize(expression):
    token_pattern = re.compile(
        r"[A-Za-z_][A-Za-z0-9_]*|[()+*]"
    )

    tokens = []
    position = 0

    while position < len(expression):
        if expression[position].isspace():
            position += 1
            continue

        match = token_pattern.match(expression, position)

        if not match:
            raise ValueError(
                f"Invalid character: {expression[position]}"
            )

        lexeme = match.group()
        position = match.end()

        if lexeme in "+*()":
            tokens.append(lexeme)
        else:
            tokens.append("id")

    return tokens + ["$"]

# ---------------- PARSING FUNCTION ----------------

def parse(expression):
    tokens = tokenize(expression)

    stack = [0]
    index = 0
    step = 1

    print("\nLALR(1) PARSING PROCESS")
    print("=" * 100)
    print(
        f"{'Step':<6}{'Stack':<35}"
        f"{'Input':<30}{'Action'}"
    )
    print("-" * 100)

    while True:
        state = stack[-1]
        current = tokens[index]

        stack_display = " ".join(map(str, stack))
        input_display = " ".join(tokens[index:])

        action = ACTION[state].get(current)

        if action is None:
            print(
                f"{step:<6}{stack_display:<35}"
                f"{input_display:<30}ERROR"
            )
            return False

        if action == "ACCEPT":
            print(
                f"{step:<6}{stack_display:<35}"
                f"{input_display:<30}ACCEPT"
            )
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

            # Remove two entries per RHS symbol
            for _ in range(2 * len(rhs)):
                stack.pop()

            state = stack[-1]
            next_state = GOTO[state][lhs]

            stack.append(lhs)
            stack.append(next_state)

            description = (
                f"Reduce {lhs} -> {' '..join(rhs)}, "
                f"goto {next_state}"
            )

        print(
            f"{step:<6}{stack_display:<35}"
            f"{input_display:<30}{description}"
        )
        step += 1

# ---------------- MAIN ----------------

print("\nLALR(1) PARSER")
print("Grammar:")
print("E -> E + T | T")
print("T -> T * F | F")
print("F -> ( E ) | id")

if conflicts:
    print("\nParsing table conflicts detected:")
    for conflict in conflicts:
        print(conflict)
else:
    print("\nGrammar is LALR(1): No parsing table conflicts.")

expression = input("\nEnter expression: ")

try:
    if parse(expression):
        print("\nResult: Expression ACCEPTED.")
    else:
        print("\nResult: Expression REJECTED.")

except (ValueError, IndexError, KeyError):
    print("\nResult: Expression REJECTED.")
