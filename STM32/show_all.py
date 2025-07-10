import gc
gc.collect()

def show_all(edge, neo, tcrt,color=[1,0,0], mode=8):
    neo.fill_edge(edge,color)
    neo.write()
    neo.fill_edge(edge,[0,0,0])
    neo.write()
    have_down, long_push = tcrt.have()
    if have_down:  # 长按退出
        return 0
    else:
        return mode  # 留在当前状态

if __name__=='__main__':
    from myneopixel import *
    from read_as5600_uart import *
    from read_TCRT import *
    
    import time
    neo=neopixel(pin_id='A0',num=240,timing=[350, 800, 700, 600])
    as5600=encoder_as5600()
    tcrt = TCRT5000(pin_id='C3')

    from big_edge import *
    flame_index=0
    old_flame_index=flame_index
    while 1:
        flame_index = as5600.read_flame(flame=36)[0]
        if old_flame_index!=flame_index:
            show_all(edge_12,color=[1,0,0])
            old_flame_index=flame_index









