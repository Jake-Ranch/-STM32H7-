from machine import Pin, bitstream
from xy2num import *
# from edge import *


class neopixel():#GRB
    def __init__(self,pin_id='G11',num=240,timing=[350, 800, 700, 600]):
        self.pin=Pin(pin_id, Pin.OUT)
        self.num=num
        self.strip=bytearray([0,0,0]*self.num)
        self.timing=timing

    def fill_rect(self,xy2num,x0=0,y0=0,x1=18,y1=18,color=[0,0,0]):#以矩形填充一片区域
        for x in range(x0,x1):#填充x0-x1
            for y in range(y0,y1):#填充y0-y1
                led_id=xy2num[x+y*18]
                self.change(led_id=led_id,color=color)
        
    def fill(self,color=[0,0,0]):#填充同一种颜色
        self.strip=bytearray(color*self.num)

    def fill_edge(self,edge,color=[0,0,0]):#填充边缘颜色#边缘可以自己选择是什么边缘
        for led_id in edge.values():
            self.change(led_id=led_id, color=color)

    def write(self):
        bitstream(self.pin, 0, self.timing, self.strip)
        
    def clear(self):#黑屏
        self.strip=bytearray([0,0,0]*self.num)
        self.write()
        
    def change(self,led_id=0,color=[0,0,0]):
        led_id*=3
        self.strip[led_id:led_id+3]=bytearray(color)

    def print_word(self,word_dict={'A':[[1, 0], [2, 0]]},word='A',color=[0,0,0],dx=0,dy=0,word_width=4,screen_x=18,screen_y=18):
        for w in word:#取出第一个字
            for p in word_dict[w]:#取出该字的点
                x=p[0]+dx
                y=p[1]+dy
                if 0<x<screen_x and 0<y<screen_y:#不能超出屏幕范围
                    led_id=xy2num[x+y*screen_x]*3
                    self.strip[led_id:led_id+3]=bytearray(color)
            dx+=word_width


        
        

if __name__=='__main__':
    import time
    from base_color import *
    from xy2num import *
#     Vcc = Pin('G13', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Vcc.value(0)
#     Gnd = Pin('G9', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Gnd.value(1)
    neo=neopixel(pin_id='A0')
#     neo=neopixel(pin_id=4)
    neo.clear()
    st=time.ticks_us()
    for j in range(36):
        for i in range(240):
            neo.change(i,white)
        neo.write()
    print((time.ticks_us()-st)/1000000)
    neo.clear()
    
    import gc
    gc.collect()
    from word3x5 import *
    
    
    time.sleep(1)
    neo.fill_rect(xy2num,x0=0,y0=0,x1=8,y1=8,color=[9,5,1])#以矩形填充一片区域
    neo.write()
    time.sleep(1)
    
    
    neo.clear()
    dx=0
    dirt=1
    try:
        while 1:
            neo.print_word(word_dict=word3x5,word='ABC123',color=[1,1,1],dx=dx,dy=5,word_width=4)
            neo.write()
            time.sleep(0.5)
            neo.print_word(word_dict=word3x5,word='ABC123',color=[0,0,0],dx=dx,dy=5,word_width=4)
            neo.write()
            if dx>10:
                dirt=-dirt
            if dx<0:
                dirt=-dirt
            dx=dx+dirt
            
    except:
        neo.clear()
    neo.clear()

