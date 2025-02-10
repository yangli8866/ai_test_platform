


class Assert():

    def c1(self):
        print("断言第一个字段")

    def c2(self):
        print("断言第一个字段")

    def c3(self):
        pass

    def c4(self):
        pass

    def all(self):
        self.c1()
        self.c2()
        self.c3()

class QK1Assert(Assert):
    def c2(self):
        print("这是一个变化的C2")


class QK2Assert(Assert):
    def c3(self):
        print("这是一个变化的C2")


class China(QK1Assert):
    def c3(self):
        print('这是一个重写的断言方法')


class America(QK2Assert):
    def c3(self):
        print('这是一个重写的断方法')

    def c4(self):
        print('')





china = China()
china.all()