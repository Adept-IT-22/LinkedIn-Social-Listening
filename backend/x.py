class Person:
    def __init__(self, name, age):
        self.age = age
        self.name = name

    def show_name(self):
        return self.name

person1 = Person("Mark", 28)

#shows you which class the object person1 belongs to
print(person1.__class__)
#shows you the attributes of the object person1
print(person1.__dict__)