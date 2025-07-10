#球坐标系，半径是9
from xy2num import *
from math import acos,pi,asin
from mynumpy import *

cube=[[2,2,4],#[x,y,z,G,R,B]
      [-3,2,4],
      [2,-3,4],
      [-3,-3,4],
      [2,2,-2],
      [-3,2,-2],
      [2,-3,-2],
      [-3,-3,-2],
      ]
# cube=[[2,2,3,1,1,1],#[x,y,z,G,R,B]
#       [-2,2,3,1,1,1],
#       [2,-2,3,1,1,1],
#       [-2,-2,3,1,1,1],
#       [2,2,-2,1,1,1],
#       [-2,2,-2,1,1,1],
#       [2,-2,-2,1,1,1],
#       [-2,-2,-2,1,1,1],
#       ]
cube_num=len(cube)#点的个数


def find_nearest_element(arr, target):#找出arr中和target最接近的值
    return min(arr, key=lambda x: abs(x - target))

def ceil(num):#向上取整
    return int(num)+1

def make_cube_p(cube,flame_num=36,G=1,B=1,R=1,mycolor=False):
    cube_p = [[] for i in range(flame_num)]  # 极坐标(直接得到36个面上的所有点和颜色信息，其中点是按xy2num转换好了的# )
    minangle = 360 // flame_num  # 最小角度
    arr = [i for i in range(0, 360, minangle)]
    for c in cube:
        if mycolor:#格式后面三个是颜色
            x,y,z,G,B,R=c
        else:
            x,y,z=c#使用默认的全白颜色
        p=abs(complex(x,y))
        theta=acos(x/p)/pi*180
        if asin(y/p)<0:
            theta+=180
        flameid=arr.index(find_nearest_element(arr, target=theta))#找出最接近的角度，并作映射

        if 0<(z+9)<18:
            if 0<9 + int(p) <18:
                lo=9+int(p)+int(z+9)*18
                lo=xy2num[lo]
                if lo != 240:  # 在圆形四角，无法显示
                    cube_p[flameid].append([lo,G,R,B])#在该帧中加入[坐标,G,R,B]
            if 0<9-ceil(p)<18:
                lo = 9-ceil(p)+int(z+9)*18
                lo = xy2num[lo]
                if lo!=240:#在圆形四角，无法显示
                    cube_p[(flameid+flame_num//2)%flame_num].append([lo,G,R,B])#在背面帧中加入[坐标,G,R,B]
    return cube_p

if __name__ == "__main__":
    flame_num = 36  # 一圈显示36张画面（360分为36角度，每个角度占10度）
    cube_p=make_cube_p(cube,flame_num=flame_num)
    print(cube_p)

