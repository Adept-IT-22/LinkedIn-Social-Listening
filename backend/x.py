dictionary = {
    "xyz": {
        "a": "aaa", 
        "b": "bbb"
    },
    "efg": {
        "e": "eee",
        "f": "fff"
    }
}

for name, values in dictionary.items():
    print(f"Name Type: {type(name)}")
    print(f"Value Type: {type(values)}")
    print(name)
    print(values)