import abc

class Shape(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def calculate_area(self):
        pass

    @abc.abstractmethod
    def calculate_perimeter(self):
        pass

class Rectangle(Shape):
    def __init__(self, height, width):
        self.height = height
        self.width = width

    def calculate_area(self):
        return self.height * self.width

    def calculate_perimeter(self):
        return 2* (self.height + self.width)

class Square(Shape):
    def __init__(self, width):
        self.width = width

    def calculate_area(self):
        return self.width * self.width

    def calculate_perimeter(self):
        return 4* self.width

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def calculate_area(self):
        return 3.14 * self.radius * self.radius

    def calculate_perimeter(self):
        return 2 * 3.14 * self.radius

class ShapeFactory:
    def create_shape(self, name):
        if name == 'circle':
            radius = input('Enter the radius of the circle: ')
            return Circle(float(radius))
        elif name == 'rectangle':
            height = input('enter the height of the rectangle: ')
            width = input(' enter the widht of the rectanggle: ')
            return Rectangle(float(height), float(width))
        elif name == 'square':
            width = input('enter the widht of the square: ')
            return Square(float(width))

if __name__ == '__main__':

    shape_factory = ShapeFactory()
    shape_name = input('enter the name of the shape: ')
    shape = shape_factory.create_shape(shape_name)

    print(f'the type of object created: {type(shape)}')
    print(f"The area of the {shape_name} is: {shape.calculate_area()}")
    print(f"The perimeter of the {shape_name} is: {shape.calculate_perimeter()}")
