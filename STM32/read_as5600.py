from machine import I2C, Pin,SoftI2C


class encoder_as5600():
    def __init__(self,sda_id='D3',scl_id='D1',round_gate=0.5):
        self.i2c = SoftI2C(sda=Pin(sda_id),scl=Pin(scl_id))
        print(self.i2c.scan())
        self.old_val=0
        self.val=0
        self.flame=0
        self.old_flame=0
        self.round=0#绕的圈数（分正负）
        self.round_gate=round_gate
        
    def read_as5600(self):
        self.old_val=self.val
        
        
        data = self.i2c.readfrom_mem(0x36, 0x0C, 2)
        raw = (data[0] << 8) | data[1]
        self.val=raw/4095

#         data1=self.i2c.readfrom_mem(0x36, 0x0C, 1, addrsize=8)#高4位
#         data2=self.i2c.readfrom_mem(0x36, 0x0D, 1, addrsize=8)#低8位
#         val1=int(hex(data1[0]),16)
#         val2=int(hex(data2[0]),16)
#         self.val=(val1*256+val2)/4095#0-1
        
        
        d_val=self.val-self.old_val
        if abs(d_val)>self.round_gate:#变化大于预设值，可认为转过了一圈
            if d_val>0:
                self.round+=1
                rev = 1  # 跨圈标志
            else:
                self.round-=1
                rev = -1  # 跨圈标志
        else:
            rev=0
        return self.val,rev#转成360度和2pi
    
    def read_flame(self,flame=22):
        val,rev=self.read_as5600()
        return int((val-0.001)*flame),rev

    def read_addsub(self,flame=22):
        self.old_flame=self.flame
        self.flame,rev=self.read_flame(flame)
        return self.flame,-flame * rev + (self.flame-self.old_flame)
    
    
if __name__=='__main__':
    import time
#     from math import pi
#     as5600=encoder_as5600(sda_id=5,scl_id=4,round_gate=0.5)
    as5600=encoder_as5600(sda_id=7,scl_id=4,round_gate=0.5)
    while 1:
#         val_360,val_2pi=as5600.read_as5600()
#         print(val*360,val*2*pi)#转成360度

#         flame,rev=as5600.read_flame(flame=36)
#         print(flame,rev)
        print(as5600.read_addsub(flame=36))
        time.sleep(0.5)
