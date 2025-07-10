from base_color import *
# which_mode= {
#             1: 1,#显示地球
#             2: 20,#倒计时设置（滚轮设置好然后确认）
#             3: 3,#显示立方体
#             4: 10,#显示秒表（停表）
#             5: 5,#显示现实时间
#             6: 6,#显示面图像
#         }
class UI():
    def __init__(self, as5600, neo,mode_dict, speed=-0.04, word_height=6, word_weight=4):
        self.as5600 = as5600
        self.neo = neo
        self.speed = speed
        self.mode_dict = mode_dict
        self.word_height = word_height  # 字体高度（含一行空格）
        self.word_weight = word_weight  # 字体宽度（含一行空格）
        self.mode_num = len(self.mode_dict) * self.word_height  # 模式数量乘字体高度，就是所有模式的总高度
        self.x_move = 0
        self.adjust_head=7#字体头部离板子左边缘的距离（数值越大距离越小）
        self.adjust_tail=-1#字体末尾离板子又边缘的距离（数值越大距离越小）
        
        maxlen = 0
        for v in self.mode_dict.values():
            if len(v) > maxlen:
                maxlen = len(v)  # 最长字符
#         self.left_len = self.word_weight * (maxlen + 1) - (18 - 5)  # 还差多少像素才能完全显示
        self.left_len = self.word_weight * (maxlen + 1) - self.adjust_head  # 还差多少像素才能完全显示,越大说明还有越多字没显示完全，整体滚动完会更慢

        self.now_mode=0

    def UI_fun(self, neo,word3x5, tcrt,xy2num):
        neo.fill()
        flame = self.as5600.read_flame(flame=self.mode_num)[0]  # 获取角度，用来设置UI上下翻滚的偏移dy
        dx = int(self.adjust_tail + self.x_move)
        now_mode=0
        for k, v in self.mode_dict.items():  # 显示模式名字
            dy=(flame + k * self.word_height) % self.mode_num
            neo.print_word(word_dict=word3x5, word=v[0], color=v[2], dx=dx,
                           dy=dy,word_width=4)
            if 3 <= dy < 3 + self.word_height:
                now_mode = k#该字处于中心，万一按下按键就选这个模式

        
        neo.fill_rect(xy2num, x0=0, y0=0, x1=5, y1=18, color=[0, 0, 0])  # 遮住前面的部分
        neo.change(xy2num[8*18],color=white)#多加一个白点
        for k in self.mode_dict.keys():  # 显示序号
            neo.print_word(word_dict=word3x5, word=str(k), color=green, dx=1,
                           dy=(flame + k * self.word_height) % self.mode_num,word_width=4)

        self.x_move = (self.x_move + self.speed) % self.left_len
        neo.write()
        
        have_down, long_push = tcrt.have()
        if now_mode!=self.now_mode:
            print('select_mode:',self.mode_dict[now_mode])
            self.now_mode=now_mode
        if have_down:  # 读取数值判断是否发生按钮按下
            return now_mode# 判断是否按下，按下则进入相应的模式，返回一个mode的编号
        else:
            return 0  # 正常情况返回0，即留在mode0


if __name__ == '__main__':
    from myneopixel import *
    from read_as5600_uart import *
    from word3x5 import *
    from read_TCRT import *
    import time
#     Vcc = Pin('G13', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Vcc.value(0)
#     Gnd = Pin('G9', Pin.OUT) # 创建一个Pin对象pe2，对应'E2'引脚配置为推挽输出
#     Gnd.value(1)
    as5600 = encoder_as5600()
    neo = neopixel(pin_id='A0')
#     neo.change(5,white)
#     neo.write()
    
    tcrt = TCRT5000(pin_id='C3', gate=0.8, overtime=5)
    ui = UI(as5600, neo, speed=-0.04, word_height=6, word_weight=4)
    while 1:
#         try:
        mode=ui.UI_fun(neo,word3x5, tcrt,xy2num)
        time.sleep_ms(10)
#         print(mode)
#         except:
#             neo.fill()
