testcases = [
    ("valid_option:", True),
    ("valid_option:\n", True),
    ("valid_option: ; inline comment", True),
    ("valid_option: # inline comment", True),
    ("valid_option :", True),
    ("valid_option=", True),
    ("valid_option= ", True),
    ("valid_option =", True),
    ("valid_option = ", True),
    ("invalid_option ==", False),
    ("invalid_option :=", False),
    ("not_a_valid_option", False),
]
