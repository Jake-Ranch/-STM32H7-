#显示各个面的数据（数据要求每个面独立开）
import gc
gc.collect()


import time

class FACE_player():#用完就del销毁，用的时候再创建
    def __init__(self,face,yellow = [2,2,0]):
        self.face=face
        self.face_num=len(self.face)
        self.face_id=0
        self.flame=self.face[self.face_id]#取出第一帧
        self.playtime=time.ticks_us()
        self.base_color=yellow

    def face_fun(self,neo,tcrt,mode=6):
        neo.fill(color=self.base_color)  # 底色
        if time.ticks_us()-self.playtime>self.flame['ti']*500000:#超时了，是时候播放下一个动画了
            self.playtime=time.ticks_us()
            self.face_id+=1
            if self.face_id>=self.face_num:#播放完毕了
                return 61#回到主界面
            self.flame = self.face[self.face_id]  # 取出下一帧
        for color,pos in self.flame['fl'].items():#将当前帧画在板子上
            for p in pos:
                neo.change(p, color=color)
        neo.write()  # 该面写入屏幕

        have_down, long_push = tcrt.have()
        if long_push:  # 长按退出
            return 0
        else:
            return mode  # 留在当前状态


# 
# if __name__=='__main__':
#     from myneopixel import *
#     from read_as5600 import *
#     from xy2num import *
#     from base_color import *
#     from read_button import *
# 
#     flame_num=36
#     Vcc = Pin('G13', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Vcc.value(0)
#     Gnd = Pin('G9', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Gnd.value(1)
# 
#     neo=neopixel(pin_id='G11',num=240,timing=[350, 800, 700, 600])
#     as5600=encoder_as5600(sda_id='D3',scl_id='D1')
#     tcrt = TCRT5000(pin_id='F9')
#     mode=6
# 
#     face_player=FACE_player(face,yellow)
#     while 1:
#         # flame_id = as5600.read_flame(flame=flame_num)[0]  # 读取目前要显示的帧
#         mode=face_player.face_fun(neo,tcrt,mode=mode)
#         print(mode)
