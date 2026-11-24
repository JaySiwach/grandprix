"""Questionnaire data and question selection.

The QUESTIONS dictionary is unchanged from the original game. Each entry is
(question text, [4 options], index of correct option, explanation).
"""
import random

from game.game_data import RACES, TOPICS

QUESTIONS = {
"print": [
("What is printed?\nprint('Turbo', 'Python')", ["Turbo Python", "TurboPython", "('Turbo', 'Python')", "Turbo,Python"], 0, "print() writes values to the console. Multiple arguments are separated by a space by default."),
("Which statement prints 25?", ["print(5 * 5)", "echo(25)", "printf(25)", "write(25)"], 0, "print() is Python's standard built-in for displaying a value."),
],
"len": [
("What is len([10, 20, 30, 40])?", ["3", "4", "5", "40"], 1, "len() returns the number of items in a container."),
("Which built-in gives the number of characters in a string?", ["count()", "size()", "len()", "chars()"], 2, "len('Python') is 6."),
],
"type": [
("What does type(3.14) return?", ["<class 'int'>", "<class 'float'>", "<class 'number'>", "float"], 1, "type() reports the object's type."),
("Which built-in checks an object's type?", ["type()", "kind()", "typeof()", "classof()"], 0, "type() returns the object's class/type."),
],
"input": [
("What does input() return by default?", ["int", "float", "str", "bool"], 2, "input() reads user input and returns it as a string."),
("Which converts entered text '25' into an integer?", ["input('25')", "int(input())", "str(input())", "float(input())"], 1, "int(input()) first reads text and then converts it to int."),
],
"range": [
("How many values are produced by list(range(2, 7))?", ["4", "5", "6", "7"], 1, "range(2, 7) produces 2, 3, 4, 5, 6."),
("Which creates 0,1,2,3,4?", ["range(1,5)", "range(5)", "range(0,4)", "range(0,5,2)"], 1, "range(5) starts at 0 and stops before 5."),
],
"int": [
("What is int('42')?", ["'42'", "42", "42.0", "Error"], 1, "int() converts compatible values to integers."),
("int(8.9) returns:", ["8", "9", "8.9", "Error"], 0, "Conversion from float to int removes the fractional part."),
],
"float": [
("What is float('3.5')?", ["3", "3.5", "'3.5'", "Error"], 1, "float() converts compatible values to floating-point numbers."),
("Which converts 7 to 7.0?", ["float(7)", "int(7)", "str(7)", "round(7)"], 0, "float(7) produces 7.0."),
],
"str": [
("What is str(123)?", ["123", "'123'", "123.0", "Error"], 1, "str() converts a value into its string representation."),
("Which converts an integer to text?", ["text()", "string()", "str()", "repronly()"], 2, "str(123) returns the string '123'."),
],
"list": [
("What is list((1, 2, 3))?", ["(1,2,3)", "[1, 2, 3]", "{1,2,3}", "Error"], 1, "list() creates a list from an iterable."),
("Which creates a list from range(3)?", ["list(range(3))", "array(range(3))", "make_list(3)", "listify(3)"], 0, "list(range(3)) gives [0, 1, 2]."),
],
"tuple": [
("What is tuple([1, 2, 3])?", ["[1,2,3]", "(1, 2, 3)", "{1,2,3}", "Error"], 1, "tuple() creates a tuple from an iterable."),
("Which is a tuple?", ["[1,2]", "(1,2)", "{1,2}", "{'a':1}"], 1, "Parentheses with comma-separated values form a tuple."),
],
"dict": [
("Which creates a dictionary?", ["{'A': 1}", "[A,1]", "(A,1)", "{A,1,2}"], 0, "A dictionary stores key-value pairs."),
("What does dict(a=1, b=2) create?", ["A list", "A tuple", "A dictionary", "A set"], 2, "dict() can construct a dictionary from keyword arguments."),
],
"set": [
("What does set([1,1,2,2]) produce?", ["{1, 1, 2, 2}", "{1, 2}", "[1,2]", "(1,2)"], 1, "Sets store unique values."),
("Which built-in creates a set?", ["unique()", "set()", "make_set()", "distinct()"], 1, "set() constructs a set."),
],
"sorted": [
("What is sorted([3,1,2])?", ["[3,1,2]", "[1,2,3]", "(1,2,3)", "3"], 1, "sorted() returns a new sorted list."),
("Which sorts without changing the original list?", ["sort()", "sorted()", "order()", "arrange()"], 1, "sorted() returns a new list; list.sort() changes the list in place."),
],
"max": [
("What is max([4,9,2])?", ["2", "4", "9", "15"], 2, "max() returns the largest item."),
("Which returns the largest value?", ["top()", "max()", "largest()", "high()"], 1, "max() returns the largest item in an iterable."),
],
"min": [
("What is min([4,9,2])?", ["2", "4", "9", "15"], 0, "min() returns the smallest item."),
("Which returns the smallest value?", ["min()", "low()", "smallest()", "bottom()"], 0, "min() returns the smallest item in an iterable."),
],
"sum": [
("What is sum([2,3,5])?", ["8", "10", "235", "5"], 1, "sum() adds numeric values in an iterable."),
("Which totals a list of numbers?", ["total()", "sum()", "addall()", "plus()"], 1, "sum() calculates the arithmetic total."),
],
"map": [
("What does map(str, [1,2]) conceptually do?", ["Filters values", "Converts each value using str", "Sorts values", "Removes values"], 1, "map() applies a function to every item."),
("Which built-in applies a function to each item?", ["map()", "each()", "applyall()", "transformonly()"], 0, "map(function, iterable) produces transformed values."),
],
"filter": [
("What does filter(is_even, nums) do?", ["Sorts nums", "Keeps items passing is_even", "Doubles nums", "Deletes all nums"], 1, "filter() keeps items for which the function is truthy."),
("Which built-in selects items satisfying a condition?", ["select()", "filter()", "choose()", "whereonly()"], 1, "filter() filters an iterable using a predicate."),
],
"zip": [
("What does zip([1,2], ['A','B']) pair?", ["1-A, 2-B", "1-2, A-B", "1-B, 2-A", "Nothing"], 0, "zip() combines corresponding items from iterables."),
("Which combines iterables position-by-position?", ["join()", "zip()", "pair()", "merge()"], 1, "zip() produces tuples of corresponding elements."),
],
"enumerate": [
("What does enumerate(['a','b']) provide?", ["Only values", "Index-value pairs", "Only indexes", "Sorted values"], 1, "enumerate() yields pairs like (0,'a'), (1,'b')."),
("Which adds indexes while iterating?", ["index()", "enumerate()", "numbered()", "counter()"], 1, "enumerate() is designed for indexed iteration."),
],
"isinstance": [
("isinstance(5, int) returns:", ["True", "False", "5", "int"], 0, "isinstance() checks whether an object is an instance of a class."),
("Which checks object/class compatibility?", ["typecheck()", "isinstance()", "sameclass()", "classof()"], 1, "isinstance(obj, class) returns a boolean."),
],
"open": [
("Which built-in opens a file?", ["file()", "open()", "readfile()", "load()"], 1, "open() opens a file and returns a file object."),
("Which mode is commonly used for writing text?", ["'r'", "'w'", "'xread'", "'scan'"], 1, "'w' opens a file for writing and may overwrite existing content."),
],
"abs": [
("What is abs(-12)?", ["-12", "12", "0", "Error"], 1, "abs() returns the absolute value."),
("What is abs(5 - 12)?", ["-7", "7", "17", "0"], 1, "5 - 12 is -7, whose absolute value is 7."),
],
"round": [
("What is round(3.6)?", ["3", "4", "3.6", "36"], 1, "round() rounds a number to the nearest precision."),
("What does round(5.678, 2) return?", ["5.6", "5.67", "5.68", "6"], 2, "The second argument specifies the number of decimal places."),
],
"pow": [
("What is pow(2, 3)?", ["5", "6", "8", "9"], 2, "pow(2,3) means 2 raised to the power 3."),
("Which is equivalent to 3 ** 4?", ["pow(3,4)", "power(3,4)", "exp(3,4)", "raise(3,4)"], 0, "pow(base, exponent) calculates exponentiation."),
],
"divmod": [
("What is divmod(17, 5)?", ["(3,2)", "(2,3)", "3.4", "12"], 0, "divmod() returns quotient and remainder."),
("Which gives quotient and remainder together?", ["splitdiv()", "divmod()", "quotrem()", "divideall()"], 1, "divmod(a,b) returns (a//b, a%b)."),
],
"bool": [
("bool(0) is:", ["True", "False", "0", "None"], 1, "Zero is considered false in a boolean context."),
("bool('Python') is:", ["True", "False", "'Python'", "Error"], 0, "A non-empty string is truthy."),
],
"bin": [
("bin(10) returns:", ["'1010'", "'0b1010'", "1010", "'10b'"], 1, "bin() returns the binary representation prefixed with 0b."),
("Which converts an integer to binary text?", ["binary()", "bin()", "base2()", "bits()"], 1, "bin() produces a binary string."),
],
"oct": [
("oct(8) returns:", ["'8'", "'0o10'", "'10o'", "10"], 1, "oct() returns octal representation prefixed with 0o."),
("Which built-in produces octal text?", ["oct()", "base8()", "octal()", "o()"], 0, "oct() converts an integer to an octal string."),
],
"hex": [
("hex(15) returns:", ["'15'", "'0xF'", "'F0'", "15"], 1, "hex() returns hexadecimal representation prefixed with 0x."),
("Which built-in produces hexadecimal text?", ["hex()", "base16()", "hexa()", "h()"], 0, "hex() converts an integer to a hexadecimal string."),
],
"chr": [
("chr(65) returns:", ["'65'", "'A'", "65", "Error"], 1, "chr() converts a Unicode code point to a character."),
("Which reverses the basic ord() operation?", ["chr()", "char()", "unicode()", "decodechar()"], 0, "chr(code_point) returns the corresponding character."),
],
"ord": [
("ord('A') returns:", ["'A'", "65", "1", "Error"], 1, "ord() returns the Unicode code point of a single character."),
("Which gets a character's code point?", ["code()", "ord()", "unicodeof()", "ascii_code()"], 1, "ord('A') is 65."),
],
"id": [
("What does id(obj) provide?", ["Object's unique identity value", "Object's type", "Object's size", "Object's text"], 0, "id() returns an integer identifying the object during its lifetime."),
("Which built-in exposes object identity?", ["identity()", "id()", "objectid()", "address()"], 1, "id() returns the identity value of an object."),
],
"hash": [
("hash('Python') returns a:", ["Hash value", "List", "Boolean only", "File"], 0, "hash() returns an integer hash value for hashable objects."),
("Which built-in creates a hash value?", ["hash()", "digest()", "checksum()", "encodehash()"], 0, "hash() computes an object's hash."),
],
"repr": [
("What is repr('hi')?", ["hi", "'hi'", "HI", "Error"], 1, "repr() returns a printable representation, including quotes for a string."),
("Which built-in gives an unambiguous representation?", ["repr()", "show()", "display()", "inspecttext()"], 0, "repr() is intended for developer-oriented representations."),
],
"format": [
("What is format(3.14159, '.2f')?", ["3.1", "3.14", "3.15", "3.14159"], 1, "format() applies a format specification to a value."),
("Which formats a value using a format specification?", ["format()", "style()", "fmt()", "render()"], 0, "format(value, spec) returns formatted text."),
],
"reversed": [
("What does list(reversed([1,2,3])) produce?", ["[1,2,3]", "[3,2,1]", "[2,1,3]", "Error"], 1, "reversed() returns an iterator that traverses an object backward."),
("Which built-in iterates in reverse order?", ["reverse()", "reversed()", "backward()", "invert()"], 1, "reversed() returns a reverse iterator."),
],
"iter": [
("What does iter([1,2]) create?", ["An iterator", "A string", "A set", "A dictionary"], 0, "iter() obtains an iterator from an iterable."),
("Which built-in gets an iterator?", ["iterator()", "iter()", "iterate()", "make_iter()"], 1, "iter(iterable) returns an iterator."),
],
"next": [
("If it = iter([10,20]), next(it) returns:", ["10", "20", "[10,20]", "Error"], 0, "next() retrieves the next item from an iterator."),
("Which built-in retrieves the next iterator value?", ["next()", "advance()", "step()", "iterate_next()"], 0, "next(iterator) gets the next item."),
],
"any": [
("any([False, False, True]) is:", ["True", "False", "1 only", "Error"], 0, "any() is true when at least one element is truthy."),
("Which checks whether at least one item is truthy?", ["any()", "some()", "exists()", "oneof()"], 0, "any() returns True if any element is truthy."),
],
"all": [
("all([True, True, False]) is:", ["True", "False", "None", "Error"], 1, "all() is true only when every element is truthy."),
("Which checks whether every item is truthy?", ["every()", "all()", "each()", "forall()"], 1, "all() returns True if all elements are truthy."),
],
"globals": [
("What does globals() provide?", ["Global namespace dictionary", "Local list", "All modules only", "Current file text"], 0, "globals() returns the current global symbol table as a dictionary."),
("Which built-in exposes the current global namespace?", ["globals()", "global()", "scope()", "namespace()"], 0, "globals() provides the global namespace dictionary."),
],
"locals": [
("What does locals() provide?", ["Current local namespace mapping", "All globals", "A list of locals", "The current filename"], 0, "locals() returns the current local symbol table."),
("Which built-in exposes the local namespace?", ["locals()", "local()", "scope()", "vars_local()"], 0, "locals() returns the current local namespace mapping."),
],
"vars": [
("vars(obj) is commonly used to access:", ["__dict__ of an object", "Only methods", "Only globals", "The object's id"], 0, "vars() without arguments acts like locals(); with an object it commonly returns __dict__."),
("Which built-in can inspect an object's __dict__?", ["vars()", "inspectdict()", "dictof()", "members()"], 0, "vars(obj) commonly returns obj.__dict__."),
],
"dir": [
("What does dir(obj) provide?", ["A list of attributes/names", "Object memory size", "Only methods", "Object value"], 0, "dir() returns a list of names available in an object/context."),
("Which built-in is commonly used to inspect available attributes?", ["dir()", "listattrs()", "members()", "inspect()"], 0, "dir() provides a useful list of names."),
],
"hasattr": [
("hasattr(obj, 'x') returns:", ["True/False", "x's value", "x's type", "x's id"], 0, "hasattr() checks whether an object has an attribute."),
("Which checks whether an attribute exists?", ["hasattr()", "existsattr()", "attribute()", "findattr()"], 0, "hasattr(obj, name) returns a boolean."),
],
"getattr": [
("What does getattr(obj, 'speed') do?", ["Gets the speed attribute", "Deletes speed", "Sets speed", "Checks callable"], 0, "getattr() retrieves an attribute by name."),
("Which built-in retrieves an attribute dynamically?", ["getattr()", "fetchattr()", "readattr()", "attrget()"], 0, "getattr(obj, name) returns the named attribute."),
],
"setattr": [
("What does setattr(car, 'speed', 200) do?", ["Sets speed to 200", "Reads speed", "Deletes speed", "Checks speed"], 0, "setattr() dynamically assigns an attribute."),
("Which built-in sets an attribute by name?", ["setattr()", "putattr()", "assignattr()", "changeattr()"], 0, "setattr(obj, name, value) sets the named attribute."),
],
"delattr": [
("What does delattr(obj, 'x') do?", ["Deletes x", "Reads x", "Creates x", "Checks x"], 0, "delattr() removes a named attribute."),
("Which built-in deletes an attribute dynamically?", ["removeattr()", "delattr()", "delete()", "clearattr()"], 1, "delattr(obj, name) deletes the named attribute."),
],
"callable": [
("callable(len) returns:", ["True", "False", "len", "Error"], 0, "Functions and other callable objects return True from callable()."),
("Which checks whether an object can be called?", ["callable()", "isfunction()", "call()", "caninvoke()"], 0, "callable(obj) returns True when the object can be called."),
],
}


# Additional question bank: 50 new questions for each of the 50 built-in topics.
# Each question tests the purpose/use of the built-in, with shuffled distractors.
BUILTIN_PURPOSES = {
    "print": "displaying text or values in the output",
    "len": "getting the number of items in a container or characters in a string",
    "type": "finding the class or data type of an object",
    "input": "reading text entered by the user from the keyboard",
    "range": "generating a sequence of integers for iteration",
    "int": "converting a compatible value to an integer",
    "float": "converting a compatible value to a floating-point number",
    "str": "converting a value to its string representation",
    "list": "creating a mutable list from an iterable",
    "tuple": "creating an immutable tuple from an iterable",
    "dict": "creating a dictionary of key-value pairs",
    "set": "creating a collection that stores unique values",
    "sorted": "returning a new list containing sorted items",
    "max": "finding the largest item in a collection",
    "min": "finding the smallest item in a collection",
    "sum": "adding the numeric items of an iterable",
    "map": "applying a function to every item in an iterable",
    "filter": "keeping only items that pass a condition",
    "zip": "combining corresponding items from multiple iterables",
    "enumerate": "iterating over values together with their indexes",
    "isinstance": "checking whether an object belongs to a specified class or type",
    "open": "opening a file to read or write its contents",
    "abs": "getting the non-negative magnitude of a number",
    "round": "rounding a number to a chosen precision",
    "pow": "calculating a number raised to a power",
    "divmod": "getting the quotient and remainder of a division together",
    "bool": "converting a value to its Boolean truth value",
    "bin": "converting an integer to a binary string",
    "oct": "converting an integer to an octal string",
    "hex": "converting an integer to a hexadecimal string",
    "chr": "converting a Unicode code point to its character",
    "ord": "getting the Unicode code point of a character",
    "id": "getting the identity value of an object",
    "hash": "getting the hash value of a hashable object",
    "repr": "getting a developer-oriented printable representation of an object",
    "format": "formatting a value according to a format specification",
    "reversed": "iterating through a sequence in reverse order",
    "iter": "obtaining an iterator from an iterable object",
    "next": "retrieving the next item from an iterator",
    "any": "checking whether at least one item in an iterable is truthy",
    "all": "checking whether every item in an iterable is truthy",
    "globals": "accessing the current global namespace dictionary",
    "locals": "accessing the current local namespace mapping",
    "vars": "accessing an object's attribute dictionary or the local namespace",
    "dir": "listing the names and attributes available on an object",
    "hasattr": "checking whether an object has a named attribute",
    "getattr": "retrieving an attribute by its name dynamically",
    "setattr": "assigning an attribute by its name dynamically",
    "delattr": "deleting an attribute by its name dynamically",
    "callable": "checking whether an object can be called like a function",
}

QUESTION_STEMS = [
    "Which Python built-in is used for {purpose}?",
    "A Python program needs to perform this task: {purpose}. Which built-in should it use?",
    "Choose the correct built-in for this operation: {purpose}.",
    "Which function from Python's built-ins best matches this requirement: {purpose}?",
    "A developer wants to do the following: {purpose}. What should they call?",
    "In Python, what built-in provides this capability: {purpose}?",
    "Select the built-in that performs this job: {purpose}.",
    "You are writing a Python script that must handle this task: {purpose}. Which function is appropriate?",
    "Which built-in name completes this requirement: {purpose}?",
    "Identify the Python built-in responsible for {purpose}.",
    "For this requirement — {purpose} — which built-in is the best choice?",
    "Which standard Python function lets a program {purpose}?",
    "A teammate needs to {purpose}. Which built-in should they use?",
    "Choose the built-in that provides the ability to {purpose}.",
    "Which built-in name matches this programming task: {purpose}?",
]

# Make the added prompts distinct while keeping the tested concept accurate.
QUESTION_CONTEXTS = [
    "This is needed in a small beginner program.",
    "This operation is performed while processing application data.",
    "The task appears inside a reusable helper function.",
    "The program must use Python's standard built-in tools.",
    "The requirement occurs during a normal script execution.",
    "Assume that no third-party package is available.",
    "The task is part of a data-processing application.",
    "The code runs as part of a command-line tool.",
    "Use a function from the Python standard built-ins.",
    "The operation is performed inside a helper function.",
]

ALL_BUILTINS = list(BUILTIN_PURPOSES)


def _build_additional_questions():
    """Create 100 distinct, answer-checked prompts for every built-in topic."""
    for key, purpose in BUILTIN_PURPOSES.items():
        correct_name = f"{key}()"
        generated = []
        for index in range(100):
            stem = QUESTION_STEMS[index % len(QUESTION_STEMS)]
            context = QUESTION_CONTEXTS[(index // len(QUESTION_STEMS)) % len(QUESTION_CONTEXTS)]
            prompt = stem.format(purpose=purpose)
            # Add a concise context note to make each generated prompt unique.
            prompt = f"{prompt}\n{context}"

            distractor_keys = [name for name in ALL_BUILTINS if name != key]
            distractors = random.Random(f"{key}-{index}").sample(distractor_keys, 3)
            options = [correct_name] + [f"{name}()" for name in distractors]
            # Shuffle options deterministically per topic/index; gameplay question
            # selection itself remains random on every checkpoint/run.
            random.Random(f"options-{key}-{index}").shuffle(options)
            correct_index = options.index(correct_name)
            generated.append((
                prompt,
                options,
                correct_index,
                f"{correct_name} is used for {purpose}."
            ))
        QUESTIONS[key].extend(generated)


_build_additional_questions()


def build_question_deck(race_index):
    """Create a fresh shuffled question deck for each topic in this Grand Prix."""
    start = RACES[race_index][1]
    deck = {}
    for _, key, _ in TOPICS[start:start + 10]:
        pool = list(QUESTIONS.get(key, []))
        if not pool:
            raise ValueError(f"No questions are available for topic: {key}")
        random.shuffle(pool)
        deck[key] = pool
    return deck


def pick_question(race_index, challenge_index, deck=None):
    """Draw a random question without replacement from the current GP deck."""
    start = RACES[race_index][1]
    # Each GP has 10 topic categories; 15 question slots cycle through those
    # categories while drawing fresh questions from each shuffled topic pool.
    topic_display, key, category = TOPICS[start + (challenge_index % 10)]
    if deck is not None:
        pool = deck.get(key, [])
        if not pool:
            raise ValueError(f"The shuffled question deck is empty for topic: {key}")
        question = pool.pop()
    else:
        pool = QUESTIONS.get(key, [])
        if not pool:
            raise ValueError(f"No questions are available for topic: {key}")
        question = random.choice(pool)

    options = list(question[1])
    correct_answer = options[question[2]]
    random.shuffle(options)
    correct_index = options.index(correct_answer)
    return (question[0], options, correct_index, question[3], key, topic_display, category)
