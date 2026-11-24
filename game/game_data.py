"""Static championship data: the 50 Python built-in topics and the 5 Grand Prix."""

# 50 built-ins from the original educational game, reorganized into 5 GPs.
TOPICS = [
    # Rookie GP
    ("print()", "print", "Fundamentals"),
    ("len()", "len", "Fundamentals"),
    ("type()", "type", "Fundamentals"),
    ("input()", "input", "Fundamentals"),
    ("range()", "range", "Fundamentals"),
    ("int()", "int", "Conversions"),
    ("float()", "float", "Conversions"),
    ("str()", "str", "Conversions"),
    ("list()", "list", "Collections"),
    ("tuple()", "tuple", "Collections"),
    # Data GP
    ("dict()", "dict", "Collections"),
    ("set()", "set", "Collections"),
    ("sorted()", "sorted", "Collections"),
    ("max()", "max", "Collections"),
    ("min()", "min", "Collections"),
    ("sum()", "sum", "Collections"),
    ("map()", "map", "Functional"),
    ("filter()", "filter", "Functional"),
    ("zip()", "zip", "Functional"),
    ("enumerate()", "enumerate", "Functional"),
    # Systems GP
    ("isinstance()", "isinstance", "Types"),
    ("open()", "open", "Files"),
    ("abs()", "abs", "Numbers"),
    ("round()", "round", "Numbers"),
    ("pow()", "pow", "Numbers"),
    ("divmod()", "divmod", "Numbers"),
    ("bool()", "bool", "Logic"),
    ("bin()", "bin", "Encoding"),
    ("oct()", "oct", "Encoding"),
    ("hex()", "hex", "Encoding"),
    # Turbo GP
    ("chr()", "chr", "Encoding"),
    ("ord()", "ord", "Encoding"),
    ("id()", "id", "Objects"),
    ("hash()", "hash", "Objects"),
    ("repr()", "repr", "Objects"),
    ("format()", "format", "Formatting"),
    ("reversed()", "reversed", "Iterators"),
    ("iter()", "iter", "Iterators"),
    ("next()", "next", "Iterators"),
    ("any()", "any", "Logic"),
    # Championship GP
    ("all()", "all", "Logic"),
    ("globals()", "globals", "Runtime"),
    ("locals()", "locals", "Runtime"),
    ("vars()", "vars", "Runtime"),
    ("dir()", "dir", "Runtime"),
    ("hasattr()", "hasattr", "Objects"),
    ("getattr()", "getattr", "Objects"),
    ("setattr()", "setattr", "Objects"),
    ("delattr()", "delattr", "Objects"),
    ("callable()", "callable", "Objects"),
]

RACES = [
    ("ROOKIE GRAND PRIX", 0, 10, "Master the Python fundamentals."),
    ("DATA GRAND PRIX", 10, 20, "Manipulate collections and functional data."),
    ("SYSTEMS GRAND PRIX", 20, 30, "Numbers, files, types and encoding."),
    ("TURBO GRAND PRIX", 30, 40, "Objects, iterators and advanced logic."),
    ("CHAMPIONSHIP GRAND PRIX", 40, 50, "Advanced runtime and object control."),
]
