from machine import ADC, Pin
import time


class TCRT5000():
    def __init__(self, pin_id='C3', gate=0.8, overtime=5):
        self.AO = ADC(Pin(pin_id))
        # self.AO.width(ADC.WIDTH_12BIT)
        #         self.AO.atten(ADC.ATTN_11DB)
        self.gate = gate  # 大于该值认为被按下
        self.st = time.time()  # 按下起始时间
        self.overtime = overtime  # 超过5秒认为长按，退出秒表回到UI主界面
        self.have_down = False

    def read(self):  # 读出0-1的数值
        return self.AO.read_u16() / 65535

    #         return self.AO.read()/4095

    def updown(self):  # 判断是否有物体接近
        if self.read() > self.gate:
            return 1
        else:
            return 0

    def have(self):  # 判断是否有物体接近（只触发一次，除非抬手）
        down = self.updown()
        if down:  # 被按下
            if not self.have_down:  # 如果未曾按下
                self.have_down = True
                self.st = time.time()  # 记录开始时间
            if (time.time() - self.st) >= self.overtime:  # 超过该时间认为长按
                self.long_push = True  # 长按
            else:
                self.long_push = False
            return False, self.long_push
        else:  # 抬手
            if self.have_down:
                self.have_down = False  # 抬手了,不算长按了
                # 之前按下过，现在抬起来了，说明一次完整的按压流程结束了，第一个返回值为True
                if not self.long_push:  # 之前没有长按，说明是短按，那么可以返回True
                    return True, False
                else:  # 长按后程序回到了UI（mode=0），那么不算短按，不能返回True
                    self.long_push = False
                    return False, False
            else:
                return False, False

    def trig(self):  # 按下单触发，只有按下一瞬间会有信号，其他时刻无信号
        down = self.updown()
        if down:  # 被按下
            if not self.have_down:  # 如果未曾按下
                self.have_down = True
                return True
            return False  # 已经被按过了，后续不能再输出True
        else:  # 抬手
            self.have_down = False  # 抬手了,不算长按了
            return False


if __name__ == '__main__':
    tcrt = TCRT5000(pin_id='C3', gate=0.8, overtime=5)
#     tcrt = TCRT5000(pin_id='C3', gate=0.8, overtime=5)
    while 1:
        print(tcrt.have())
        print(tcrt.read())
        time.sleep(0.5)
