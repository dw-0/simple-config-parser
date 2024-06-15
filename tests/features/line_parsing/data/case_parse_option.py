testcases = [
    ("option: value", "option", "value"),
    ("option : value", "option", "value"),
    ("option :value", "option", "value"),
    ("option= value", "option", "value"),
    ("option = value", "option", "value"),
    ("option =value", "option", "value"),
    ("option: value\n", "option", "value"),
    ("option: value # inline comment", "option", "value"),
    ("option: value # inline comment\n", "option", "value"),
]
