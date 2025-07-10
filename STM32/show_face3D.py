import gc
gc.collect()
import time

from big_edge import *
big_edge.reverse()
class FACE3D_player():#用完就del销毁，用的时候再创建
    def __init__(self,face3D,yellow = [2,2,0]):
        self.face=face3D
        self.face_num=len(self.face)
        self.face_id=0
        self.flame=self.face[self.face_id]#取出第一帧
        self.playtime=time.time()
        self.base_color=yellow


    def face_fun(self,flame_index,neo,tcrt,mode=61):
        ed=self.flame['ed']
        neo.fill_edge(big_edge[self.face_id],color=self.base_color)    
        if time.time()-self.playtime>self.flame['ti']:#超时了，是时候播放下一个动画了
            self.playtime=time.time()
            self.face_id+=1
            if self.face_id>=self.face_num:#播放完毕了
                return 0#回到主界面
            neo.fill()
            self.flame = self.face[self.face_id]  # 取出下一帧
            gc.collect()
        cp=self.flame['fl'][flame_index]
        for color,pos in cp.items():#取出颜色和位置
            for p in pos:
                neo.change(p,color)
        neo.write()
        for color,pos in cp.items():#取出颜色和位置
            for p in pos:
                neo.change(p,[0,0,0])
        neo.write()
        have_down, long_push = tcrt.have()
        if have_down:  # 短按退出（因为在高速旋转，一般情况下周围没有物体，有东西说明该停了）
            return 0
        else:
            return mode  # 留在当前状态

if __name__ == '__main__':
    from machine import I2C, ADC, Pin, bitstream, Timer
    import time
    from read_as5600_gpio import *
    from myneopixel import *
    from base_color import *
    from motor_pwm import *
    from read_TCRT import *
    from face3D_img import *
    import gc

    have_cul = False
    flame_num = 24

    # runtime = 0  # 当前模式运行了多久（到时间了就换动画）
    now_mode = mode = 0  # 切换模式（动画）
    old_flame_index = flame_index = 0
    neo = neopixel(pin_id='A0', num=240, timing=[350, 800, 700, 600])
    # as5600=encoder_as5600(sda_id='D3',scl_id='D1')
    as5600 = encoder_as5600()
    tcrt = TCRT5000(pin_id='C3')
    
    
    
    face_player = FACE3D_player(face3D, yellow)
    have_cul = True
    flame_index = old_flame_index=0
    
    
    while 1:
        flame_index = as5600.read_flame(flame=flame_num)[0]
        if flame_index != old_flame_index:
            old_flame_index=flame_index
            now_mode = face_player.face_fun(flame_index,neo, tcrt, mode=mode)
            if mode != now_mode:  # 有改变
                have_cul = False
                mode = now_mode
                print('退出3D球形动画...', gc.mem_free() / 1024)
                del face_player, face3D, FACE3D_player
                gc.collect()
                print('退出完毕', gc.mem_free() / 1024)
    
    
    
