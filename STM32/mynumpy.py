# import math
from math import pi,sin,cos,pow,sqrt
# pi = math.pi
class Matrix(object):
    # 矩阵类
    def __init__(self, n: int, m: int, matrix=None):
        self.n = n#行[1]
        self.m = m#列[1][8]
        self.shape = (n, m)
        if (matrix):
            self.matrix = matrix
        else:
            self.matrix = [[0 for i in range(m)] for j in range(n)]

    def __add__(self, other: "Matrix"):#矩阵和矩阵相加
        # if (self.get_size() != other.get_size()):
        if (self.n != other.n or self.m != other.m):
            print("矩阵大小不匹配")
            return
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = self.matrix[i][j] + other.matrix[i][j]
        return new

    def __sub__(self, other: "Matrix"):#矩阵和矩阵相减
        # if (self.get_size() != other.get_size()):
        if (self.n != other.n or self.m != other.m):
            print("矩阵大小不匹配")
            return
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = self.matrix[i][j] - other.matrix[i][j]
        return new

    def __mul__(self, other: float):#求矩阵和常量的乘法
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = self.matrix[i][j] * other
        return new

    def __truediv__(self, other:float):#求矩阵除一个常量
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = self.matrix[i][j] / other
        return new

    def add(self, other:float):#求矩阵和一个常量相加
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = self.matrix[i][j] + other
        return new

    def sum(self):#求矩阵内所有元素的和
        sum_num=0
        for i in range(self.n):
            for j in range(self.m):
                sum_num+=self.matrix[i][j]
        return sum_num

    def pow(self):#求矩阵的各个元素平方的和
        pow_num = 0
        for i in range(self.n):
            for j in range(self.m):
                pow_num += pow(self.matrix[i][j],2)
        return pow_num

    def get_mod(self):
        return sqrt(self.pow())
        # mod_num = 0
        # for i in range(self.n):
        #     for j in range(self.m):
        #         mod_num += pow(self.matrix[i][j],2)
        # return sqrt(mod_num)

    def abs(self):#矩阵内各个元素单独求绝对值
        new = Matrix(self.n, self.m)
        for i in range(self.n):
            for j in range(self.m):
                new.matrix[i][j] = abs(self.matrix[i][j])
        return new

    def dot(self, other: "Matrix"):#两个矩阵点乘（矩阵乘法）
        if (self.m != other.n):
            print("矩阵大小不匹配")
            return
        new = Matrix(self.n, other.m)
        for i in range(self.n):
            for j in range(other.m):
                sum = 0
                for k in range(self.m):
                    sum += self.matrix[i][k] * other.matrix[k][j]
                new.matrix[i][j] = sum
        return new

    def mul(self, other: "Matrix"):#两个矩阵逐元素相乘
        if (self.n != other.n or self.m != other.m):
            print("矩阵大小不匹配")
            return
        new = Matrix(self.n, other.m)
        for i in range(self.n):
            for j in range(other.m):
                new.matrix[i][j] = self.matrix[i][j] * other.matrix[i][j]
        return new

class R_and_T():
    def __init__(self,cube):
        # self.R_T=Matrix(4, 4, [[1, 0, 0,0], [0, 1, 0,0], [0, 0, 1,0],[0,0,0,0]])
        self.R=Matrix(3, 3, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        datax = []
        datay = []
        dataz = []
        self.len_cube = len(cube)
        for c in cube:
            datax.append(c[0])
            datay.append(c[1])
            dataz.append(c[2])
        self.data=Matrix(3,self.len_cube, [datax, datay, dataz])

    def Ro(self,alpha,gamma,beta):
        self.R.matrix[0][0]=cos(gamma)*cos(beta)
        self.R.matrix[0][1]=sin(alpha)*sin(gamma)*cos(beta)-cos(alpha)*sin(beta)
        self.R.matrix[0][2]=sin(alpha)*sin(gamma)*cos(beta)+cos(alpha)*sin(beta)
        self.R.matrix[1][0]=cos(gamma)*sin(beta)
        self.R.matrix[1][1]=sin(alpha)*sin(gamma)*sin(beta)+cos(alpha)*cos(beta)
        self.R.matrix[1][2]=sin(alpha)*sin(gamma)*cos(beta)-sin(alpha)*cos(beta)
        self.R.matrix[2][0]=-sin(gamma)
        self.R.matrix[2][1]=sin(alpha)*cos(gamma)
        self.R.matrix[2][2]=cos(alpha)*cos(gamma)
        return self.R.dot(self.data)

    def Tr(self,a,b,c):
        self.T=Matrix(3,self.len_cube,[[a]*self.len_cube,[b]*self.len_cube,[c]*self.len_cube])
        return self.data+self.T

if __name__ == "__main__":
    a=Matrix(1,3,[[1,2,3]])
    b=Matrix(1,3,[[4,5,6]])
    c=Matrix(3,1,[[-1],[2],[-3]])

    # print(a.pow())
    # print(a.sum())
    # print(c.abs().matrix)
    # print((a-b).matrix)
    # print((a/0.5).matrix)

    cube = [[2, 2, 3, 1, 1, 1],  # [x,y,z,G,R,B]
            [-2, 2, 3, 1, 1, 1],
            [2, -2, 3, 1, 1, 1],
            [-2, -2, 3, 1, 1, 1],
            [2, 2, -2, 1, 1, 1],
            [-2, 2, -2, 1, 1, 1],
            [2, -2, -2, 1, 1, 1],
            [-2, -2, -2, 1, 1, 1],
            ]

    # print(a.dot(c).matrix)

    r=R_and_T(cube)
    # print(r.data.matrix)
    # print(r.data.matrix[0])

    r.data.matrix[0][1]=5
    # print(r.data.matrix[0])
    print(r.data.matrix)

    print(r.Ro(pi/2,0,0).matrix)#轴尖对着自己，逆时针绕x轴转90度

    print(r.Tr(5,0,-10).matrix)#平移


    #进行r.R_T.dot(r.data)
    # print(r.R_T.matrix)
    # datax=[]
    # datay=[]
    # dataz=[]
    # len_cube=len(cube)
    # for c in cube:
    #     datax.append(c[0])
    #     datay.append(c[1])
    #     dataz.append(c[2])
    # data_x = Matrix(len_cube, 1, [datax])
    # data_y = Matrix(len_cube, 1, [datay])
    # data_z = Matrix(len_cube, 1, [dataz])

