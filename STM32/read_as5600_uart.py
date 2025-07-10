from machine import I2C, Pin, SoftI2C, UART
import json
from pyb import LED
import re

class encoder_as5600():
    def __init__(self, round_gate=0.5):
        self.uart = UART(2, baudrate=921600, bits=8, parity=None, stop=1)  # 设置串口号2和波特率
#         self.uart = UART(1, 115200)  # 设置串口号2和波特率
        #         self.i2c = SoftI2C(sda=Pin(sda_id),scl=Pin(scl_id))
        #         print(self.i2c.scan())
        self.old_val = 0
        self.val = 0
        self.flame = 0
        self.old_flame = 0
        self.round = 0  # 绕的圈数（分正负）
        self.round_gate = round_gate  # 一次性绕过多少算一圈（默认突变半圈以上，认为转过了一周）

    def uart_send_motor(self, text='speed:20'):
        message = '>{}<\n'.format(text)
        data = ''
        while 1:
            if '>' in data and '<' in data:  # 格式完整
                print('格式完整')
                da=data.split('>')
                ta=data.split('<')
                try:
                    for ma in range(1,min(len(da),len(ta))):
                        data = da[ma].split('<')[0]  # 取出><之间的数据(str
                        if data!='':#匹配到数据了，不是空数据
                            break
                    return data
                except:
                    print('json转换错误',data)
                    return data
            elif self.uart.any():#格式不完整，可能是没接收完
                
                text = self.uart.read(1024)  # 接收128个字符
                print('接收中',text)
                data += text.decode('utf-8')
            else:#串口没数据了，但是格式不完整
                self.uart.write(message.encode('utf-8'))  # 发送一条数据
                return ''
    
    def receive_list(self):
        buffer = bytearray()
        while True:
            if self.uart.any():  # 检查是否有数据
                chunk = self.uart.read(1)  # 逐字节读取
                if chunk == b'\n':  # 检测结束符
                    break
                buffer.extend(chunk)
            else:
                break
        json_str = buffer.decode('utf-8')  # 字节转字符串
        return json.loads(json_str)  # 反序列化

    def get_pc_uart(self,text='snake:0'):
        buffer = bytearray()
        message = '>{}<\n'.format(text)
        while True:
            if self.uart.any():  # 检查是否有数据
                chunk = self.uart.read(1)  # 逐字节读取
                if chunk == b'\n':  # 检测结束符
                    break
                buffer.extend(chunk)
            else:
                self.uart.write(message.encode('utf-8'))  # 发送一条数据
        json_str = buffer.decode('utf-8')  # 字节转字符串
        return json.loads(json_str)  # 反序列化
    
       
#         self.uart.write(message.encode('utf-8'))  # 发送一条数据
#         return self.receive_list()
        
    def get_uart(self, text='as5600:0'):
        message = '>{}<\n'.format(text)
        data = ''
        while 1:
            if '>' in data and '<' in data:  # 格式完整
                da=data.split('>')
                ta=data.split('<')
#                 print(min(len(da),len(ta)),da,ta,data)
                try:
                    for ma in range(1,min(len(da),len(ta))):
                        data = da[ma].split('<')[0]  # 取出><之间的数据(str
#                         print('?',data)
                        if data!='':#匹配到数据了，不是空数据
                            data = json.loads(data)  # 转成原本格式
                            break
                    return data
                except:
                    print('json转换错误',data)
                    return ''
            elif self.uart.any():#格式不完整，可能是没接收完
                text = self.uart.read(1024)  # 接收128个字符
                data += text.decode('utf-8')
            else:#串口没数据了，但是格式不完整
                self.uart.write(message.encode('utf-8'))  # 发送一条数据
                return ''

    def get_raw(self):  # 串口获取数据
        data = self.get_uart()
        if data!='':
            self.val = data / 4095
            

    def read_as5600(self):
        self.old_val = self.val
        self.get_raw()
#         data = self.i2c.readfrom_mem(0x36, 0x0C, 2)
#         raw = (data[0] << 8) | data[1]
#         self.val=raw/4095
        d_val = self.val - self.old_val
        if abs(d_val) > self.round_gate:  # 变化大于预设值，可认为转过了一圈
            if d_val > 0:
                self.round += 1
                rev = 1  # 跨圈标志
            else:
                self.round -= 1
                rev = -1  # 跨圈标志
        else:
            rev = 0
        return self.val, rev  # 0-1和跨圈标志

    def read_flame(self, flame=22):
        val, rev = self.read_as5600()
        return int((val - 0.001) * flame), rev

    def read_addsub(self, flame=22):
        self.old_flame = self.flame
        self.flame, rev = self.read_flame(flame)
        return self.flame, -flame * rev + (self.flame - self.old_flame)


if __name__ == '__main__':
    import time

    #     from math import pi
    as5600 = encoder_as5600(round_gate=0.5)
    while 1:
        #         val_360,val_2pi=as5600.read_as5600()
        #         print(val*360,val*2*pi)#转成360度

        #         flame,rev=as5600.read_flame(flame=36)
        #         print(flame,rev)
#         as5600.read_addsub(flame=36)
        print(as5600.read_addsub(flame=36))
        time.sleep_ms(100)


