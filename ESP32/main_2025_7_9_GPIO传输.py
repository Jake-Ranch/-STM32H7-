from machine import Pin, PWM, SoftI2C, UART
from math import pi, sqrt, cos, sin
import sys
import uselect
import _thread
import time
import json
import gc
import re
import random
from neopixel import NeoPixel

#板载LED
NUMBER_PIXELS = 1
strip = NeoPixel(Pin(48), NUMBER_PIXELS)

brightness=2#亮度
green = [0, brightness, 0]#GRB
red = [brightness, 0, 0]
blue = [0, 0, brightness]
black = [0, 0, 0]  # 黑色
white = [brightness, brightness, brightness]  # 白色
grey = [brightness//2, brightness//2, brightness//2]  # 灰色
yellow = [brightness,brightness, 0]#黄色
purple= [brightness, 0, brightness]#青色
cyan=[0, brightness, brightness]#紫色
khaki=[brightness,brightness,brightness//2]#卡其色
orange=[brightness,brightness//2,0]

mode_color={0:blue,1:yellow,2:orange,3:purple,4:red}
mode=1#上电就进入的模式
fix_angle_zero=2.64#2.9
mode_angle={0:6.19,1:fix_angle_zero,2:fix_angle_zero,3:fix_angle_zero,4:fix_angle_zero}
#0:5.53
# ====================== 硬件配置 ======================
freq=20000
M1 = PWM(Pin(9), freq=freq, duty=0)  # A相
M2 = PWM(Pin(10), freq=freq, duty=0)  # B相
M3 = PWM(Pin(8), freq=freq, duty=0)  # C相
i2c = SoftI2C(scl=Pin(4), sda=Pin(7))

# ====================== 初始化方式 ====================
fix_init=True#是否要固定数值初始化
wifi_PC=False#是否开启wifi
# ====================== 控制参数 ======================
PP = 7  # 极对数
DIR = 1  # 旋转方向
VOLTAGE_LIMIT = 6.0  # 电压限制(V)
INTEGRAL_LIMIT = 3.0  # 积分限幅(V)

# 速度环PID参数
VEL_KP = 0.9
VEL_KI = 0.0
VEL_KD = 0.0

# 位置环PID参数
POS_KP = 3.3
POS_KI = 0.133
POS_KD = 0.0

# 棘轮PID参数
jilun_KP = 0.1
jilun_KI= 0
jilun_KD = 100
dead_zone=0#死区（正负x度）

# 定角PID参数(位置闭环)
angle_KP = 0.1#0.133


CTRL_FREQ = 2000  # 控制频率(Hz)
CTRL_PERIOD = 1 / CTRL_FREQ
PRINT_FREQ = 10  # 打印频率(Hz)
PRINT_PERIOD = 1 / PRINT_FREQ

attractor_distance = 45 * pi / 180.0#每45度为一档

##定义编码器GPIO口
li=[45,38,42,37,40,36,39,35,41,46,47,48]#D15,D14,...D0#跳过D1\D3\D5\D7
li.reverse()
pins = [Pin(i, Pin.OUT) for i in li]  # GPIO0-GPIO11

# 定义音符频率（基于标准音高）
notes_list = {
    '1': 2620,  # Do
    '2': 2940,  # Re
    '3': 3300,  # Mi
    '4': 3490,  # Fa
    '5': 3920,  # Sol
    '6': 4400,  # La
    '7': 4940,  # Si
    '8': 100  # 无用音符
}

# 定义歌曲《小星星》的音符和时值
song = [('8', 0.1),
    ('1', 1), ('8', 0.1), ('1', 1), ('5', 1), ('8', 0.1), ('5', 1), ('6', 1), ('8', 0.1), ('6', 1), ('5', 2),
    ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 1), ('8', 0.1), ('2', 1), ('1', 2),
    ('5', 1), ('8', 0.1), ('5', 1), ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 2),
    ('5', 1), ('8', 0.1), ('5', 1), ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 2),
    ('1', 1), ('8', 0.1), ('1', 1), ('5', 1), ('8', 0.1), ('5', 1), ('6', 1), ('8', 0.1), ('6', 1), ('5', 2),
    ('4', 1), ('8', 0.1), ('4', 1), ('3', 1), ('8', 0.1), ('3', 1), ('2', 1), ('8', 0.1), ('2', 1), ('1', 2)
]


if wifi_PC:
    from wifi import *

class CascadeController:
    def __init__(self,song=song,music_speed=4):
        self.zero_electric_angle = 0.0
        self.target_angle= pi/2#期望到达的角度（弧度）
        self.target_speed = 40.0  # 目标速度(rad/s)
        self.target_position = 0.0  # 内环目标位置(rad)
        self.current_position = 0.0
        self.motor_target = 0.0  # 棘轮目标位置(rad)
        self.current_speed = 0.0
        self.last_angle = 0.0
        self.last_time = time.ticks_us()
        self.print_time = time.ticks_us()

        # 速度环PID变量
        self.vel_integral = 0.0
        self.vel_prev_error = 0.0

        # 位置环PID变量
        self.pos_integral = 0.0
        self.pos_prev_error = 0.0
        
        #棘轮积分项
        self.jilun_error_I=0.0
        self.old_error=0

        # 编码器校准
        self.align_sensor(mode_angle[mode])

        #音乐播放
        self.song_id = 0
        self.music_time = time.ticks_us()
        self.music_speed = music_speed
        _, self.music_long = song[self.song_id]  # 音符和时长
        self.music_long /= self.music_speed
        
        #串口传输as5600
        self.uart = UART(2, 115200, rx=2, tx=1, bits=8, parity=None, stop=1)  # 设置串口号2和波特率
        self.data = ''
        self.raw=0
        
        self.zero_electric_angle_angle=2.59
        self.zero_electric_angle_speed=1.26
        
        if wifi_PC:
            self.client_init()

    def get_mean(self,lst):
        return sum(lst)/len(lst)
    
    def get_var(self,lst):
        mean=self.get_mean(lst)
        var=0
        for i in lst:
            var+=(i-mean)**2
        return var/len(lst)
        
#     def align_sensor(self):
#         self.zero_electric_angle = 6.20
#         mech_angle_list=[]
#         mech_angle=0
#         """编码器初始校准"""
#         self.set_phase_voltage(3.0, 0.0)
#         time.sleep(5)
#         for me in range(500):
#             mech_angle_list.append(self.get_mechanical_angle())
#         while self.get_var(mech_angle_list)>0.01: 
#             mech_angle = self.get_mechanical_angle()
#             mech_angle_list.pop(0)
#             mech_angle_list.append(mech_angle)
# #             self.uart_as5600(mode)#检测一下是否有数据
#         del mech_angle_list
#         gc.collect()
#         self.zero_electric_angle = self._normalize_angle(DIR * PP * mech_angle)
#         self.set_phase_voltage(0, 0)
#         print(f"Zero electric angle: {self.zero_electric_angle:.2f} rad")
#         self.last_angle = mech_angle

    
    def align_sensor(self,zero_electric_angle):
        """编码器初始校准"""
        if fix_init:
            self.zero_electric_angle = zero_electric_angle
        else:
            self.set_phase_voltage(3.0, 0.0)
            time.sleep(5)
            mech_angle = self.get_mechanical_angle()
            self.zero_electric_angle = self._normalize_angle(DIR * PP * mech_angle)
            self.set_phase_voltage(0, 0)
            print(f"Zero electric angle: {self.zero_electric_angle:.2f} rad")

        

    def _normalize_angle(self, angle):
        """角度归一化到[0, 2π]"""
        return angle % (2 * pi)

    def write_12bit(self,value):
        for i in range(12):
            pins[i].value((value >> i) & 1)  # 提取第i位并写入
                    
    def get_mechanical_angle(self):
        """读取机械角度"""
        try:
            data = i2c.readfrom_mem(0x36, 0x0C, 2)
            self.raw = (data[0] << 8) | data[1]
            self.write_12bit(self.raw)
        except:
            pass
        return self.raw / 4095 * 2 * pi

    def update_speed_position(self):
        """更新速度和位置"""
        self.current_position = self.get_mechanical_angle()
        now = time.ticks_us()
        dt = time.ticks_diff(now, self.last_time) * 1e-6

        if dt > 0:
            raw_diff = (self.current_position - self.last_angle) % (2 * pi)
            if raw_diff > pi: raw_diff -= 2 * pi
            self.current_speed = raw_diff / dt
            self.last_angle = self.current_position
            self.last_time = now

    def _electrical_angle(self):
        """计算当前电角度"""
        mech_angle = self.get_mechanical_angle()
        return self._normalize_angle(DIR * PP * mech_angle - self.zero_electric_angle)

    def set_phase_voltage(self, Uq, Ud):
        """设置相电压"""
        angle_el = self._electrical_angle()

        Ualpha = -Uq * sin(angle_el)
        Ubeta = Uq * cos(angle_el)

        Ua = Ualpha
        Ub = (-Ualpha + sqrt(3) * Ubeta) / 2
        Uc = (-Ualpha - sqrt(3) * Ubeta) / 2

        max_volt = max(abs(Ua), abs(Ub), abs(Uc))
        if max_volt > VOLTAGE_LIMIT:
            scale = VOLTAGE_LIMIT / max_volt
            Ua *= scale
            Ub *= scale
            Uc *= scale

        M1.duty(int((Ua + VOLTAGE_LIMIT) / (2 * VOLTAGE_LIMIT) * 1023))
        M2.duty(int((Ub + VOLTAGE_LIMIT) / (2 * VOLTAGE_LIMIT) * 1023))
        M3.duty(int((Uc + VOLTAGE_LIMIT) / (2 * VOLTAGE_LIMIT) * 1023))

    def velocity_control(self, target_speed):
        """速度环PID控制"""
        self.update_speed_position()

        # 速度误差
        error = target_speed - self.current_speed

        # PID计算
        proportional = VEL_KP * error

        # 积分项
        self.vel_integral += VEL_KI * error * CTRL_PERIOD
        self.vel_integral = max(min(self.vel_integral, INTEGRAL_LIMIT), -INTEGRAL_LIMIT)

        # 微分项
        derivative = VEL_KD * (error - self.vel_prev_error) / CTRL_PERIOD
        self.vel_prev_error = error

        # 速度环输出作为位置环的目标位置增量
        position_increment = proportional + self.vel_integral + derivative

        # 更新位置环目标
        self.target_position += position_increment * CTRL_PERIOD

        return self.target_position

    def position_control(self, target_position):
        """位置环PID控制"""
#         current_pos = self.get_mechanical_angle()

        # 位置误差（考虑圆周）
        error = target_position
        if error > pi: error -= 2 * pi

        # PID计算
        proportional = POS_KP * error

        # 积分项
        self.pos_integral += POS_KI * error * CTRL_PERIOD
        self.pos_integral = max(min(self.pos_integral, INTEGRAL_LIMIT), -INTEGRAL_LIMIT)

        # 微分项
        derivative = POS_KD * (error - self.pos_prev_error) / CTRL_PERIOD
        self.pos_prev_error = error

        Uq = proportional + self.pos_integral + derivative
        Uq = max(min(Uq, VOLTAGE_LIMIT), -VOLTAGE_LIMIT)

        self.set_phase_voltage(Uq, 0)
        return Uq

    def cascade_control(self, target_speed):
        """串级PID控制"""
        # 外环：速度环
        pos_target = self.velocity_control(target_speed)

        # 内环：位置环
        control_voltage = self.position_control(pos_target)

        return control_voltage

    def jilun_position_control(self, target_angle, KP=0.133):
        """修正后的位置闭环控制"""
        current_angle = self.get_mechanical_angle()

        # 修正1：正确的误差计算（移除DIR）
        error = (target_angle - current_angle) * 180 / pi

        # 修正2：添加误差归一化处理
        error = (error + 180) % 360 - 180  # 限制在[-180,180]度
        
        
        if abs(error)<dead_zone:error=0
        # 修正3：更保守的控制参数
        
        self.jilun_error_I+=error

        Uq = -KP * error -jilun_KI*self.jilun_error_I* CTRL_PERIOD-jilun_KD*(error-self.old_error)* CTRL_PERIOD
        Uq = max(min(Uq, VOLTAGE_LIMIT), -VOLTAGE_LIMIT)

        self.old_error=error
        self.set_phase_voltage(Uq, 0)
#         print(f"Target: {target_angle:.2f} | Current: {current_angle:.2f} | Error: {error:.1f}° | Uq: {Uq:.2f}V")

    def music_player(self):
        if (start_time - self.music_time)  > 1000000*self.music_long:  # 达到预设时长
            self.song_id += 1
            if self.song_id >= len(song):  # 唱完了
                M1.freq(freq)
                M2.freq(freq)
                M3.freq(freq)
                M1.duty(0)
                M2.duty(0)
                M3.duty(0)
                self.song_id = 0  # 把音符设置为第一个
                return False#播放结束
            note, self.music_long = song[self.song_id]  # 音符和时长
            M1.duty(0)
            M2.duty(0)
            M3.duty(0)
            self.music_long /= self.music_speed
            fre = notes_list[note]#取出这个音符的频率
            self.music_time = time.ticks_us()
            M1.freq(fre)
            M2.freq(fre)
            M3.freq(fre)
        return True#继续播放


    def client_init(self):
        ssid_password = {
            "1001": "13650100663"
                         }
        wifi_connect_list(ssid_password)
        print('wifi连接成功')
        self.client = CLIENT(port=9000, ipv4='101.33.233.95')
        print('PC端连接成功')
        
        
#     def uart_recv(self):
#         if '>' in self.data and '<' in self.data:  # 格式完整
#             data=self.data.split('>')[1].split('<')[0]
#             self.data=''
#             return data
# 
#         elif self.uart.any():#格式不完整，可能是没接收完
#             text=self.uart.read(1024)
#             if '>' in text and '<' in text:
#                 match = re.search(rb'>(.*?)<', text)
#                 text=match.group(1)
# 
#                 self.data += text.decode('utf-8')
#             return ''
#             
#         else:#串口没数据了，但是格式不完整
#             return ''



        
    def uart_recv(self):
        if self.uart.any():#串口有数据
            text=self.uart.read(2048)
#             print(text)
            try:
                match = re.search(rb'>(.*?)<', text)
                text=match.group(1)
                data = text.decode('utf-8')
            except:
                data=''
            return data
        else:#串口没数据了，但是格式不完整，或者压根没人发过来
            return ''

#     def uart_recv(self):
#         buffer = bytearray()
#         while True:
#             if self.uart.any():  # 检查是否有数据
#                 chunk = self.uart.read(1)  # 逐字节读取
#                 if chunk == b'\n':  # 检测结束符
#                     json_str = buffer.decode('utf-8')  # 字节转字符串
#                     return json.loads(json_str)  # 反序列化
#                 buffer.extend(chunk)
#                 print(self.uart.any())
#             else:
#                 return ''#压根没人发过来

#     def uart_recv(self):
#         if self.uart.any():
#             buffer=self.uart.read(2048)
#             print(buffer)
#             json_str = buffer.decode('utf-8')  # 字节转字符串
#             return json.loads(json_str)  # 反序列化
#         else:
#             return ''#压根没人发过来
        
            
    def uart_as5600(self,mode):
        data=self.uart_recv()
        new_mode=mode
        global attractor_distance
        if data!='':
            mode_name,arg=data.split(':')
#             print(mode_name,arg,self.raw)
            message=data
#             if mode_name == 'as5600':  # 获取编码器数据的
#                 message = self.raw  # 返回角度数据0-4095
            if mode_name=='speed':#恒速
                self.target_speed=int(arg)
                new_mode=0
            elif  mode_name=='angle':#角度
                self.target_angle=int(arg)* pi / 180
                new_mode=2
            elif  mode_name=='music':#音乐
                new_mode=3
            elif  mode_name=='stop':#停止
                new_mode=4
            elif  mode_name=='button':#棘轮旋钮
                new_mode=1
                attractor_distance=int(arg)* pi / 180.0#弧度
            elif mode_name == 'snake':  # 发给PC端
                if wifi_PC:
                    self.client.send(data.encode('utf-8'))  # 将发送的数据进行编码
                    print('ESP32已发送TCP数据到PC端!')
                    message = self.client.recv(1024)  # 接受服务端的信息，最大数据为1k
    #                 message=json.loads(message)  # 反序列化
                else:
                    cube_p=[{}, {'1,1,1': [167, 160, 132, 125, 96, 89, 63, 56]}, {}, {'1,1,1': [168, 165, 162, 159, 133, 127, 124, 97, 94, 91, 88, 64, 61, 58, 55], '0,0,1': [130]}, {}, {'1,1,1': [167, 132, 125, 96, 89, 63, 56], '1,1,0': [160]}, {}, {'1,1,1': [167, 160, 132, 125, 96, 89, 63, 56]}, {}, {'1,1,1': [168, 165, 162, 159, 133, 127, 124, 97, 94, 91, 88, 64, 61, 58, 55], '0,1,0': [130]}, {}, {'1,1,1': [167, 160, 125, 96, 89, 63, 56], '0,1,0': [132]}, {}, {'1,1,1': [160, 167, 125, 132, 89, 96, 56, 63]}, {}, {'1,1,1': [159, 162, 165, 168, 124, 130, 133, 88, 91, 94, 97, 55, 58, 61, 64], '0,0,1': [127]}, {}, {'1,1,1': [160, 125, 132, 89, 96, 56, 63], '1,1,0': [167]}, {}, {'1,1,1': [160, 167, 125, 132, 89, 96, 56, 63]}, {}, {'1,1,1': [159, 162, 165, 168, 124, 130, 133, 88, 91, 94, 97, 55, 58, 61, 64], '0,1,0': [127]}, {}, {'1,1,1': [160, 167, 132, 89, 96, 56, 63], '0,1,0': [125]}]
                    message=json.dumps(cube_p)+'\n'
                self.uart.write(message.encode('utf-8'))  # 返回数据给STM
#                 json_bytes = message.encode('utf-8')  # 转换为字节
                
#                 message=json.loads(message)  # 反序列化
                print('ESP32收到PC端TCP数据：',message)
                return new_mode
            message='>{}<\n'.format(message)
            self.uart.write(message.encode('utf-8'))  # 返回数据给STM
#             print('ESP32发送串口数据到STM32：', message)
        return new_mode
        

        


# def read_serial_input():
#     """非阻塞读取串口输入"""
#     spoll = uselect.poll()
#     spoll.register(sys.stdin, uselect.POLLIN)
#     if spoll.poll(0):
#         return sys.stdin.readline().strip()
#     return None


# ====================== 主程序 ======================
if __name__ == "__main__":
#     if 0:_thread.start_new_thread(client_fun, ())
    strip[0]=green
    strip.write()
    
    controller = CascadeController()
    
    print("串级PID控制已启动")
    print("速度环PID: KP=%.3f, KI=%.3f, KD=%.3f" % (VEL_KP, VEL_KI, VEL_KD))
    print("位置环PID: KP=%.3f, KI=%.3f, KD=%.3f" % (POS_KP, POS_KI, POS_KD))
    strip[0]=mode_color[mode]
    strip.write()
    try:
        while True:
            start_time = time.ticks_us()

            if mode==0:#恒速控制
                control_voltage = controller.cascade_control(controller.target_speed)
            elif mode==1:#棘轮旋钮
                controller.jilun_position_control(controller.motor_target, KP=jilun_KP)
                controller.motor_target = (round(controller.get_mechanical_angle() / attractor_distance) * attractor_distance)
            elif mode==2:# 执行位置闭环控制
                controller.jilun_position_control(target_angle=controller.target_angle, KP=angle_KP)#arg=40 * pi / 180
            elif mode==3:#播放音乐
                if controller.song_id%10==0:
                    controller.jilun_position_control(target_angle=random.randint(0,10)+90)
                music_end=controller.music_player()
                if not music_end:#音乐播放完毕，回到主界面
                    M1.freq(freq)
                    M2.freq(freq)
                    M3.freq(freq)
                    mode=1
            elif mode == 4:  # 停止
                M1.duty(0)
                M2.duty(0)
                M3.duty(0)

            
            new_mode=controller.uart_as5600(mode)#检测一下是否有数据
            if new_mode!=mode:#改变模式了，需要重新初始化
                M1.duty(0)
                M2.duty(0)
                M3.duty(0)
                if mode==0:
                    controller.align_sensor(mode_angle[mode])
                else:
                    controller.align_sensor(mode_angle[mode])
                mode=new_mode
                strip[0]=mode_color[mode]
                strip.write()
                if mode==2 or mode==1:#清空积分项
                    controller.jilun_error_I=0
                
            
#             # 3. 低频打印（10Hz）
#             if time.ticks_diff(time.ticks_us(), controller.print_time) * 1e-6 >= PRINT_PERIOD and mode==0:
#                 print("目标速度: {:.2f} | 实际速度: {:.2f} | 目标位置: {:.2f} | 实际位置: {:.2f} | Uq: V".format(
#                     controller.target_speed, controller.current_speed,
#                     controller.target_position, controller.current_position))
#                 controller.print_time = time.ticks_us()



            
                    
                    
            # 4. 严格周期控制
            elapsed = time.ticks_diff(time.ticks_us(), start_time) * 1e-6
            if elapsed < CTRL_PERIOD:
                time.sleep(CTRL_PERIOD - elapsed)



            
    except KeyboardInterrupt:
        M1.duty(0)
        M2.duty(0)
        M3.duty(0)
        print("\n电机已停止")
        strip[0]=red
        strip.write()
        _thread.exit()





















