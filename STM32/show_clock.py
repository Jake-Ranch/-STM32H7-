from clock import *
import time
from base_color import *
from word3x5 import *
from machine import RTC


class CLOCK():
    def __init__(self):
        self.minute_total = 0
        self.new_hour = 0
        self.new_minute = 0
        self.old_minute_60 = 0
        self.old_hour_24 = 0
        self.rtc = RTC()
        self.old_real_minute = 0
        self.old_real_hour = 0
        self.old_real_second = 0
        self.old_cont_minute = 0
        self.old_cont_second = 0
        self.old_cont_m_second = 0
        self.count_now = self.rtc.datetime()
        st = self.rtc.datetime()
        self.st_m_second = st[-1] // 1000 + 1000 * st[-2] + 60000 * st[-3]
        # self.rtc.datetime((2025, 5, 27, 2, 0, 0, 0, 0))  # 设置时间：年+月+日+星期+时+分+秒+毫秒，不设置则按当前的现实世界时间计算


    def stop_watch_fun(self, neo, tcrt, mode):
        # 秒表（按下确认键开始，由于不涉及电机，这里就直接进while 1了，第一次清零，第二次开始，第三次停止，三循环。长按退出该模式回到mode0）
        if mode == 10:  # 清零状态
            neo.fill()
            st = self.rtc.datetime()
            self.st_m_second = st[-1] // 1000 + 1000 * st[-2] + 60000 * st[-3]
            neo.print_word(word_dict=word3x5, word='0:', color=white, dx=2, dy=3, word_width=4)
            neo.print_word(word_dict=word3x5, word='00', color=white, dx=9, dy=3, word_width=4)
            neo.print_word(word_dict=word3x5, word='.000', color=white, dx=1, dy=10, word_width=4)
            neo.write()
            have_down, long_push = tcrt.have()
            if long_push:  # 长按退出
                return 0
            else:
                if have_down:  # 读取数值判断是否发生按钮按下
                    return 11  # 开始计时
                else:
                    return mode  # 留在当前状态
        elif mode == 11:  # 计时状态，显示秒
            neo.fill()
            now = self.rtc.datetime()

            now_m_second = now[-1] + 1000 * now[-2] + 60000 * now[-3]
            cont = now_m_second - self.st_m_second
            cont_minute = (cont // 60000) % 10
            cont_second = ('0' + str((cont // 1000) % 60))[-2:]
            cont_m_second = ('00' + str(cont % 1000))[-3:]

            neo.print_word(word_dict=word3x5, word='{}:'.format(self.old_cont_minute), color=black, dx=2, dy=3,
                           word_width=4)
            neo.print_word(word_dict=word3x5, word='{}'.format(self.old_cont_second), color=black, dx=9, dy=3,
                           word_width=4)
            neo.print_word(word_dict=word3x5, word='.{}'.format(self.old_cont_m_second), color=black, dx=1, dy=10,
                           word_width=4)

            neo.print_word(word_dict=word3x5, word='{}:'.format(cont_minute), color=white, dx=2, dy=3, word_width=4)
            neo.print_word(word_dict=word3x5, word='{}'.format(cont_second), color=white, dx=9, dy=3, word_width=4)
            neo.print_word(word_dict=word3x5, word='.{}'.format(cont_m_second), color=white, dx=1, dy=10, word_width=4)

            self.old_cont_minute = cont_minute
            self.old_cont_second = cont_second
            self.old_cont_m_second = cont_m_second

            neo.write()

            have_down, long_push = tcrt.have()
            if long_push:  # 长按退出
                return 0
            else:
                if have_down:  # 读取数值判断是否发生按钮按下
                    return 12  # 开始计时
                else:
                    return mode  # 留在当前状态

        elif mode == 12:  # 停表，显示秒,不需要改变，等待按表即可
            have_down, long_push = tcrt.have()
            if long_push:  # 长按退出
                return 0
            else:
                if have_down:  # 读取数值判断是否发生按钮按下
                    return 10  # 开始计时
                else:
                    return mode  # 留在当前状态

    def real_clock(self, neo, tcrt,word3x5,mode=5):  # 正常按现实时间走
        tim = self.rtc.datetime()
        # rtc.datetime((2025, 5, 27, 2, 19, 22, 36, 0))  # 设置时间：年+月+日+星期+时+分+秒+毫秒，不设置则按当前的现实世界时间计算
        month = ('0' + str(tim[1]))[-2:]
        day = ('0' + str(tim[2]))[-2:]
        ho = tim[-4]
        mi = tim[-3]
        se = tim[-2]

        real_hour = int(((ho * 60 + mi) // 15) % 48)
        real_minute = int(mi / 60 * 48)
        real_second = int(se / 60 * 48)

        if ho >= 12:
            neo.print_word(word_dict=word3x5, word='A', color=black, dx=5, dy=11)  # 把A涂黑
            neo.print_word(word_dict=word3x5, word='PM', color=cyan, dx=5, dy=11)

        else:
            neo.print_word(word_dict=word3x5, word='P', color=black, dx=5, dy=11)  # 把P涂黑
            neo.print_word(word_dict=word3x5, word='AM', color=orange, dx=5, dy=11)

        neo.print_word(word_dict=word3x5, word=month, color=yellow, dx=1, dy=5, word_width=4)
        neo.print_word(word_dict=word3x5, word='.', color=white, dx=6, dy=6, word_width=4)
        neo.print_word(word_dict=word3x5, word=day, color=purple, dx=10, dy=5, word_width=4)

        if self.old_real_hour != real_hour:
            neo.change(hour[self.old_real_hour], color=black)
        neo.change(hour[real_hour], color=red)

        if self.old_real_minute != real_minute:
            neo.change(minute[self.old_real_minute], color=black)
        neo.change(minute[real_minute], color=green)

        neo.change(second[self.old_real_second], color=black)
        neo.change(second[real_second], color=blue)

        self.old_real_hour = real_hour
        self.old_real_minute = real_minute
        self.old_real_second = real_second
        neo.write()

        have_down, long_push = tcrt.have()
        if long_push:  # 长按退出
            return 0
        return mode


    def set_clock_fun(self, as5600, neo, tcrt, mode):  # 旋钮设置倒计时间
        if mode == 20:
            minute_total = self.minute_total
            if 1:
                _, addsub = as5600.read_addsub(flame=60)
            else:
                addsub = 1
            minute_total += addsub
            hour_24 = (minute_total // 60)%12
            hour_4 = (minute_total // 15) % 48  # 15分钟+1
            minute_60 = minute_total % 60
            new_minute = minute[int(minute_60 / 60 * 48)]
            new_hour = hour[int(hour_4)]
            if addsub:  # 有变化
                neo.fill()
                for v in scale_hour.values():
                    neo.change(v, white)#基本表盘
                neo.print_word(word_dict=word3x5,word=':',
                               color=cyan, dx=7, dy=5, word_width=4)
                neo.print_word(word_dict=word3x5,
                               word='{}{}'.format(('0' + str(hour_24))[-2:], ('0' + str(minute_60))[-2:]),
                               color=yellow, dx=1, dy=5, word_width=4)
                
                neo.change(new_minute, green)
                neo.change(new_hour, red)
                
                neo.write()
                self.old_minute_60 = minute_60
                self.old_hour_24 = hour_24
                self.minute_total = minute_total
                self.new_hour = new_hour
                self.new_minute = new_minute
            have_down, long_push = tcrt.have()
            if long_push:  # 长按退出
                self.new_hour = 0
                self.new_minute = 0
                self.old_minute_60 = 0
                self.old_hour_24 = 0
                return 0
            else:
                if have_down:  # 读取数值判断是否发生按钮按下
                    count_now = self.rtc.datetime()
                    self.count_now = count_now[4] * 60 + count_now[5]
                    return 21  # 开始倒计时
                else:
                    return mode  # 留在当前状态


        elif mode == 21:  # 倒计时开始
            now = self.rtc.datetime()
            # rtc.datetime((2025, 5, 27, 2, 19, 22, 36, 0))  # 设置时间：年+月+日+星期+时+分+秒+毫秒
            now_time = now[4] * 60 + now[5]#计算出时间
            # 从倒计时开始到当前时刻的总分钟，那么还有 self.minute_total-pass_time要等
            pass_time = (now_time - self.count_now) % 1440
            left_time=self.minute_total-pass_time
#             print('还剩:',pass_time,now_time,self.count_now,self.minute_total,self.rtc.datetime())
            if pass_time < self.minute_total:  # 倒计的时间还没到
                hour_24 = left_time // 60
                hour_4 = (left_time // 15) % 48  # 15分钟+1
                minute_60 = left_time % 60
                new_minute = minute[int(minute_60 / 60 * 48)]
                new_second = second[int((59-now[-2])/59*47)]
                new_hour = hour[int(hour_4)]

                neo.fill()
                for v in scale_hour.values():
                    neo.change(v, white)
                neo.print_word(word_dict=word3x5,word=':',
                               color=cyan, dx=7, dy=5, word_width=4)
                neo.print_word(word_dict=word3x5,
                               word='{}{}'.format(('0' + str(hour_24))[-2:], ('0' + str(minute_60))[-2:]),
                               color=yellow, dx=1, dy=5, word_width=4)
                
                neo.change(new_minute, green)
                neo.change(new_hour, red)
                neo.change(new_second, blue)
                
                
                neo.write()
                self.old_minute_60 = minute_60
                self.old_hour_24 = hour_24

            else:  # 倒计时时间到
                print('To Bell')
                return 22  # 进入闹铃

            self.new_hour = new_hour
            self.new_minute = new_minute

            have_down, long_push = tcrt.have()
            if long_push:  # 长按退出
                self.new_hour = 0
                self.new_minute = 0
                self.old_minute_60 = 0
                self.old_hour_24 = 0
                return 0
            else:
                if have_down:  # 读取数值判断是否发生按钮按下
                    return 20  # 重新设置倒计时时间
                else:
                    return mode  # 留在当前状态

if __name__ == '__main__':
    from read_TCRT import *
    from myneopixel import *
    from read_as5600_gpio import *
    from xy2num import *


    as5600 = encoder_as5600()
    neo = neopixel(pin_id='A0')
    clock = CLOCK()
    tcrt = TCRT5000(pin_id='C3', gate=0.8, overtime=5)
    neo.clear()

    if 0:
        while 1:
            print(clock.rtc.datetime())
            time.sleep(0.5)

    else:
        mode = 20
        while 1:
#             mode=clock.real_clock(neo,tcrt,word3x5,mode=5)
#             mode=clock.stop_watch_fun(neo,tcrt,mode)
            print(mode)
            mode = clock.set_clock_fun(as5600, neo, tcrt, mode)
            if mode == 0 or mode == 22:
                neo.clear()
                break
            time.sleep(0.2)
