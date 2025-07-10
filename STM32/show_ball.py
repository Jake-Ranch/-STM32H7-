import gc
gc.collect()
# from edge_12 import *

def ball_fun(neo,tcrt,edge,flame,mode=61):
    neo.fill_edge(edge,color=[2,2,0])
    for color,pos in flame.items():#取出颜色和位置
        for p in pos:
            neo.change(p,color)
    neo.write()
    have_down, long_push = tcrt.have()
    if have_down:  # 短按退出（因为在高速旋转，一般情况下周围没有物体，有东西说明该停了）
        return 0
    else:
        return mode  # 留在当前状态
