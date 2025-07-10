# 移植自: 正点原子W25QXX驱动代码	
from machine import SPI, Pin
from micropython import const
import gc
import time

__TYPE = dict(
    W25Q80 = 0XEF13,
    W25Q16 	= 0XEF14,
    W25Q32 	= 0XEF15,
    W25Q64 	= 0XEF16,
    W25Q128    = 0XEF17,
)

MEM_SIZE = {
    0XEF13 : 1000000,
    0XEF14 : 2000000,
    0XEF15 : 4000000,
    0XEF16 : 8000000,
    0XEF17 : 16000000,
}

# 指令表
W25X_WriteEnable		= const(0x06)
W25X_WriteDisable		= const(0x04)
W25X_ReadStatusReg		= const(0x05)
W25X_WriteStatusReg		= const(0x01)
W25X_ReadData			= const(0x03)
W25X_FastReadData		= const(0x0B)
W25X_FastReadDual		= const(0x3B)
W25X_PageProgram		= const(0x02)
W25X_BlockErase			= const(0xD8)
W25X_SectorErase		= const(0x20)
W25X_ChipErase			= const(0xC7)
W25X_PowerDown			= const(0xB9)
W25X_ReleasePowerDown	= const(0xAB)
W25X_DeviceID			= const(0xAB)
W25X_ManufactDeviceID	= const(0x90)
W25X_JedecDeviceID		= const(0x9F)

class __W25QXX:
    def __init__(self, SPI, CS_PIN):
        self.__SPI = SPI
        self.__CS_PIN = CS_PIN
        self.read(0 ,1)
        self.TYPE = self.__readID()
        # self.TYPE = 0XEF15
        self.__MEM = MEM_SIZE[self.TYPE]
        if self.TYPE in list(__TYPE.values()):
            print("W25QXX type is " + list(__TYPE.keys())[list(__TYPE.values()).index(self.TYPE)])
        else: print("unknown device")
    # 写一个字节
    def __writeByte(self, b):
        self.__SPI.write(bytearray([b]))
    # 读取状态寄存器
    def __readSR(self):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_ReadStatusReg]))
        ret = list(self.__SPI.read(1))
        self.__CS_PIN.on()
        return ret[0]
    # 写状态寄存器
    def __writeSR(self, sr):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_WriteStatusReg]))
        self.__SPI.write(bytearray([(sr)]))
        self.__CS_PIN.on()
    # W25QXX写使能	
    # 将WEL置位   
    def __writeEnable(self):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_WriteEnable]))
        self.__CS_PIN.on()
    # W25QXX写禁止	
    # 将WEL清零  
    def __writeDisable(self):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_WriteDisable]))
        self.__CS_PIN.on()
    # 读取芯片ID
#     def __readID(self):
#         self.__CS_PIN.off()
#         self.__SPI.write(bytearray([0x90 ,0 ,0 ,0]))
#         tmp = list(self.__SPI.read(2))
#         return (tmp[0]<<8 )+ tmp[1]
    
    def __readID(self):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([0x90, 0, 0, 0]))
        tmp = list(self.__SPI.read(2))
        self.__CS_PIN.on()
        print("Device ID bytes:", tmp)  # 调试信息
        return (tmp[0] << 8) + tmp[1]
    # 读取SPifLASH  
    # 在指定地址开始读取指定长度的数据
    # pBuffer:数据存储区
    # ReadAddr:开始读取的地址(24bit)
    # NumByteToRead:要读取的字节数(最大65535)    
    def read(self, addr, num):
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_ReadData, (addr>>16 ) &0xff, (addr>>8 ) &0xff ,addr &0xff]))
        ret = self.__SPI.read(num)
        self.__CS_PIN.on()
        return ret
    
    
    # SPI在一页(0~65535)内写入少于256个字节的数据
    # 在指定地址开始写入最大256字节的数据
    # pBuffer:数据存储区
    # WriteAddr:开始写入的地址(24bit)
    # NumByteToWrite:要写入的字节数(最大256),该数不应该超过该页的剩余字节数!!!
    def __writePage(self, buff, addr, num):
        self.__writeEnable()
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_PageProgram, (addr>>16 ) &0xff, (addr>>8 ) &0xff, addr &0xff]))
        self.__SPI.write(buff[:num])
        self.__CS_PIN.on()
        self.__waitBusy()
    # 无检验写SPifLASH 
    # 必须确保所写的地址范围内的数据全部为0XFF,否则在非0XFF处写入的数据将失败!
    # 具有自动换页功能 
    # 在指定地址开始写入指定长度的数据,但是要确保地址不越界!
    # pBuffer:数据存储区
    # WriteAddr:开始写入的地址(24bit)
    # NumByteToWrite:要写入的字节数(最大65535)
    # CHECK OK
    # 等待空闲
    def __writeNoCheck(self, buff, addr, num):
        pageremain = 256- addr %256
        if(num <= pageremain): pageremain = num
        while True:
            self.__writePage(buff, addr, pageremain)
            if(num == pageremain): break
            else:
                buff = buff[pageremain:]
                gc.collect()
                addr += pageremain
                num -= pageremain
                if num > 256: pageremain = 256
                else: pageremain = num
                # 写SPifLASH
    # 在指定地址开始写入指定长度的数据
    # 该函数带擦除操作!
    # pBuffer:数据存储区
    # WriteAddr:开始写入的地址(24bit)						
    # NumByteToWrite:要写入的字节数(最大65535)  
    def write(self, buff, addr, num):
        buff_tmp = None
        secpos = addr // 4096
        secoff = addr % 4096
        secremain = 4096 - secoff
        if num <= secremain: secremain = num
        while True:
            #             print("...")
            buff_tmp = bytearray(self.read(secpos * 4096, 4096))
            if sum(map(lambda x : x^ 0xff, buff_tmp[secoff:])):  # 需要擦除
                # if True: # 需要擦除
                self.__eraseSector(secpos)
                for i in range(0, secremain):
                    buff_tmp[i + secoff] = buff[i]
                self.__writeNoCheck(buff_tmp, secpos * 4096, 4096)
            else:
                self.__writeNoCheck(buff, secpos * 4096, 4096)
            if num == secremain:
                break  # 写入结束
            else:
                secpos += 1
                secoff = 0
                buff = buff[secremain:]
                addr += secremain
                if num > 4096:
                    secremain = 4096
                else:
                    secremain = num
            gc.collect()

    # 擦除整个芯片		  
    # 等待时间超长...
    def eraseChip(self):
        self.__writeEnable()
        self.__waitBusy()
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_ChipErase]))
        self.__CS_PIN.on()
        self.__waitBusy()

    # 擦除一个扇区
    # Dst_Addr:扇区地址 根据实际容量设置
    # 擦除一个扇区的最少时间:150ms
    def __eraseSector(self, addr):
        #         print("erase sector : {0:}".format(addr))
        addr *= 4096
        self.__writeEnable()
        self.__waitBusy()
        self.__CS_PIN.off()
        self.__SPI.write(bytearray([W25X_SectorErase, (addr >> 16) & 0xff, (addr >> 8) & 0xff, addr & 0xff]))
        self.__CS_PIN.on()
        self.__waitBusy()

    # 等待空闲
    def __waitBusy(self):
        while True:
            if self.__readSR() & 0x01 == 0x01:
                time.sleep_ms(5)
            else:
                break


# block device 接口
class W25QXX_BlockDev(__W25QXX):
    def __init__(self, SPI, CS_PIN):
        self.block_size = 4096
        super().__init__(SPI, CS_PIN)
        super().read(0, 1)
        # self.data = bytearray(block_size * num_blocks)

    def readblocks(self, block_num, buf):
        buf_tmp = self.read(block_num * self.block_size, len(buf))
        for i in range(len(buf)):
            buf[i] = buf_tmp[i]

    def writeblocks(self, block_num, buff):
        self.write(buff, block_num * self.block_size, len(buff))

    def ioctl(self, op, arg):
        if op == 4:  # get number of blocks
            return self.__MEM // self.block_size
        if op == 5:  # get block size
            return self.block_size

if __name__=='__main__':
    from machine import  Pin, SoftSPI,SPI
    import uos,os
    import ujson
    import gc
    spi = SoftSPI(baudrate=10000000, polarity=1, phase=1, sck=Pin('F10'), mosi=Pin('F8'), miso=Pin('F9'))
#     spi = SoftSPI(baudrate=10000000, polarity=1, phase=1, sck=Pin('F10'), mosi=Pin('F9'), miso=Pin('F8'))
    cs = Pin('G6', Pin.OUT)
    wp=Pin('F7',Pin.OUT)
    hold=Pin('F6',Pin.OUT)
    wp.value(1)
    hold.value(1)
    flash = W25QXX_BlockDev(SPI = spi, CS_PIN = cs)
#     print(flash,flash.readblocks(0,[0,0,0,0]))
#     os.VfsFat.mkfs(flash)#新建文件夹必须运行一遍这个，后面可以不再运行这行
    os.mount(flash, '/f')#手动创建一个名字叫f的文件夹
    print('挂载成功')
    
    
    large_list = [5,1,3,6,2]*500  # 示例数据
#     data_to_write = bytearray(large_list)  # 将列表转换为字节数组

    
    st=time.ticks_us()
    with open('/f/data1.txt', 'w')as f:
        f.write(ujson.dumps(large_list))
#         f.write(ujson.dumps(data_to_write))
    print('存储时间：',(time.ticks_us() - st)/1000000)
    del large_list
    gc.collect()
    
    



    large_list2 = [2,6,3,1,5] * 200  # 示例数据
#     data_to_write2 = bytearray(large_list2)  # 将列表转换为字节数组

    st = time.ticks_us()
    with open('/f/data2.txt', 'w')as f:
        f.write(ujson.dumps(large_list2))
    print('存储时间：', (time.ticks_us() - st) / 1000000)
    del large_list2
    gc.collect()
    
    
    
    
    st = time.ticks_us()
    with open('/f/data1.txt', 'r') as f:
        data=f.read()
    print(data)
    gc.collect()
    print('读取时间：', (time.ticks_us() - st)/1000000)
    
    
    
    st = time.ticks_us()
    with open('/f/data2.txt', 'r') as f:
        data = f.read()
    print(data)
    gc.collect()
    print('读取时间：', (time.ticks_us() - st) / 1000000)


    # data = {
    #     "CPU": "ESP32",
    #     "Flash": "Flash Test"}
    #
    # st = time.ticks_us()
    # with open('/f/info.txt', 'w')as f:
    #     f.write(ujson.dumps(data))
    # print('存储时间：', time.ticks_us() - st)
    # #
    # st = time.ticks_us()
    # with open('/f/info.txt', 'r') as f:
    #     d = ujson.loads(f.read())
    # print(d)
    # print('读取时间：', time.ticks_us() - st)

    # flash.writeblocks()


    # # 写入数据到 W25Q64
    # write_data(0, data_to_write)  # 将数据写入到地址 0
    #
    # # 从 W25Q64 读取数据
    # read_data_from_flash = read_data(0, len(data_to_write))
    #
    # # 将读取的数据转换回列表
    # read_list = list(read_data_from_flash)
    # read_list = list(read_data_from_flash)

    
    
    
    
    
    
    

