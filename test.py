import pickle
# TEST FOR DATA DUMP/ LOAD


class TestObject:
    def __init__(self) -> None:
        self.naam = "steve"

    def sayName(self):
        print(self.naam)


steve = TestObject()
steve.sayName()

# with open('steve', 'wb') as output:
#     pickle.dump(steve, output, pickle.HIGHEST_PROTOCOL)
#     output.close()

# del steve

with open('steve', 'rb') as input:
    thomas = pickle.load(input)
    thomas.sayName()
