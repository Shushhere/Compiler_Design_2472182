import re

# List of keywords
keywords = {
    "int", "float", "char", "double", "if", "else",
    "while", "for", "return", "void", "break", "continue"
}

# Token patterns
token_patterns = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATOR", r"==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|[+\-*/%=<>]"),
    ("SEPARATOR", r"[();{},\[\]]"),
    ("SKIP", r"[ \t\n]+"),
    ("INVALID", r".")
]

pattern = re.compile("|".join(
    f"(?P<{name}>{regex})" for name, regex in token_patterns
))

def lexical_analysis(source):
    print("\nLEXICAL ANALYSIS")
    print("-" * 50)
    print(f"{'LEXEME':<15} {'TOKEN TYPE':<20}")
    print("-" * 50)

    for match in pattern.finditer(source):
        token_type = match.lastgroup
        lexeme = match.group()

        if token_type == "SKIP":
            continue

        if token_type == "IDENTIFIER" and lexeme in keywords:
            token_type = "KEYWORD"

        print(f"{lexeme:<15} {token_type:<20}")

    print("-" * 50)


# Main program
source_code = input("Enter source code: ")
lexical_analysis(source_code)
