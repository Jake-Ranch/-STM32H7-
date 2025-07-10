import gc
gc.collect()

def earth_fun(flame,neo,tcrt,mode=1):
    for color,pos in flame.items():#取出颜色和位置
        for p in pos:
            neo.change(p,color)#color
    neo.write()
    for color,pos in flame.items():#取出颜色和位置
        for p in pos:
            neo.change(p,[0,0,0])
    neo.write()
    have_down, long_push = tcrt.have()
    if have_down:  # 短按退出（因为在高速旋转，一般情况下周围没有物体，有东西说明该停了）
        return 0
    else:
        return mode  # 留在当前状态

if __name__=='__main__':
    from earth_img import *
    from myneopixel import *
    from read_as5600_uart import *
    from read_TCRT import *
    import time
    
    neo=neopixel(pin_id='A0',num=240,timing=[350, 800, 700, 600])
    as5600=encoder_as5600()
    tcrt = TCRT5000(pin_id='C3')


    mode=1
    flame_index=0
    old_flame_index=flame_index
    while 1:
        flame_index = as5600.read_flame(flame=36)[0]
        if old_flame_index!=flame_index:
            flame=noon[flame_index]
            mode=earth_fun(flame,neo,tcrt,mode=mode)
            old_flame_index=flame_index






