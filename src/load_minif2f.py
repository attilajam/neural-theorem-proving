def load_theorems(path):
    with open(path, "r") as f:
        theorems = f.read().split("\n\n")
    return theorems

def load_imports(path):
    with open(path, "r") as f:
        imports = f.read()
    return imports
