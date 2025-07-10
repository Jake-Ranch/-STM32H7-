# 定义音符频率（基于标准音高）
notes_list ={'1': 5, '2': 7, '3': 9, '4': 11, '5': 13, '6': 15, '7': 17, '8': 1}
notes_bar={'5': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75, 92, 93, 111, 110, 128, 129, 147, 146, 163, 164, 180, 179], '4': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75, 92, 93, 111, 110, 128, 129, 147, 146], '7': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75, 92, 93, 111, 110, 128, 129, 147, 146, 163, 164, 180, 179, 194, 195, 209, 208, 221, 222, 232, 231], '6': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75, 92, 93, 111, 110, 128, 129, 147, 146, 163, 164, 180, 179, 194, 195, 209, 208], '1': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44], '8': [2, 1], '3': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75, 92, 93, 111, 110], '2': [2, 1, 7, 8, 18, 17, 30, 31, 45, 44, 59, 60, 76, 75]}

color_bar=[[2, 5, 1], [1, 4, 3], [4, 5, 3], [1, 5, 3], [5, 1, 2], [1, 4, 2], [4, 1, 1], [5, 3, 3], [1, 5, 4], [5, 1, 1], [5, 3, 5], [3, 3, 1], [4, 3, 1], [5, 2, 2], [1, 4, 1], [3, 4, 1], [5, 1, 5], [5, 5, 2]]
# 定义歌曲《小星星》的音符和时值
song = [('8', 0.1),
    ('1', 1), ('8', 0.1), ('1', 1), ('5', 1), ('8', 0.1), ('5', 1), ('6', 1), ('8', 0.1), ('6', 1), ('5', 2),
    ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 1), ('8', 0.1), ('2', 1), ('1', 2),
    ('5', 1), ('8', 0.1), ('5', 1), ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 2),
    ('5', 1), ('8', 0.1), ('5', 1), ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 2),
    ('1', 1), ('8', 0.1), ('1', 1), ('5', 1), ('8', 0.1), ('5', 1), ('6', 1), ('8', 0.1), ('6', 1), ('5', 2),
    ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 1), ('8', 0.1), ('2', 1), ('1', 2)
]
import time
def music_show(neo):
    for so in song:
        notes,lon=so
        neo.fill()
        bar=notes_bar[notes]
        for ba in range(0,len(bar),2):
            neo.change(bar[ba],color_bar[ba//2])
            neo.change(bar[ba+1],color_bar[ba//2])
        neo.write()
        time.sleep_ms(int(lon*250))
    neo.clear()
        
        
if __name__ == '__main__':
    import random
    notes_bar={}
    color_bar=[]
    while len(color_bar)<18:
        color=[]
        for j in range(3):
            color.append(random.randint(0,8))
        if color not in color_bar:
            color_bar.append(color)
        
    from xy2num import *
    for k,v in notes_list.items():
        for i in range(v):
            pos=xy2num[9+18*(17-i)]
            pos1=xy2num[8+18*(17-i)]
#             print(k,pos,pos1)
            if k in notes_bar.keys():
                notes_bar[k].append(pos)
                notes_bar[k].append(pos1)
            else:
                notes_bar[k]=[pos,pos1]
    print('notes_bar',notes_bar)
    
    print('color_bar',color_bar)
    
    
    
    from machine import I2C, ADC, Pin, bitstream, Timer
    import time
    from read_as5600_gpio import *
    # from read_as5600_uart import *
    from myneopixel import *
    from base_color import *
    from motor_pwm import *
    from read_TCRT import *
    import gc

    have_cul = False
    # flame_num=36
    flame_num = 24

    # runtime = 0  # 当前模式运行了多久（到时间了就换动画）
    now_mode = mode = 0  # 切换模式（动画）
    old_flame_index = flame_index = 0
    neo = neopixel(pin_id='A0', num=240, timing=[350, 800, 700, 600])
    # as5600=encoder_as5600(sda_id='D3',scl_id='D1')
    as5600 = encoder_as5600()
    tcrt = TCRT5000(pin_id='C3')
        

    music_show(neo)