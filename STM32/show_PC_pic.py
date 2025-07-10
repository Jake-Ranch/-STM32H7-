import gc
gc.collect()


def show_pc_fun(flame,neo,tcrt,mode=61):
    # if flame!='':#有数据
    for color_str,pos in flame.items():#取出颜色和位置
        
        color=list(map(int,color_str.split(',')))
        for p in pos:
            neo.change(p,color)
    neo.write()
    for _,pos in flame.items():#取出颜色和位置
        for p in pos:
            neo.change(p,[0,0,0])
    neo.write()

    have_down, long_push = tcrt.have()
    if have_down:  # 短按退出（因为在高速旋转，一般情况下周围没有物体，有东西说明该停了）
        return 0
    else:
        return mode  # 留在当前状态




