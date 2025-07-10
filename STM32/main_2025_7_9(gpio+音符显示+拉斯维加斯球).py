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
# 
# # from machine import Pin,I2C,SoftI2C
# def test():
# #     for i in [38,37,36,35,34,33,21,18,17,16,15,14]:
# #         globals()[f'pin{i}']=Pin(i,Pin.IN)
# #     st=time.ticks_us()
# #     buffer = bytearray()
# #     for i in [38,37,36,35,34,33,21,18,17,16,15,14]:
# #         buffer.extend('{}'.format(Pin(i).value()))
# #     binary_str = buffer.decode('ascii')  # 转为字符串 "101101101110"
# #     decimal_value = int(binary_str, 2)
# #     print(time.ticks_us()-st,decimal_value)
#     li=[38,37,36,35,34,33,21,18,17,16,15,14]
#     i2c = SoftI2C(scl=Pin(4), sda=Pin(7))
#     for i in li:
#         globals()[f'pin{i}']=Pin(i,Pin.OUT)
#         
#         
#     st=time.ticks_us()
#     data = i2c.readfrom_mem(0x36, 0x0C, 2)
#     raw = (data[0] << 8) | data[1]
# 
#     buffer=('0'*11+bin(raw)[2:])[-12:]
#     for i in range(12):
#         globals()['pin{}'.format(li[i])].value(int(buffer[i]))
#     print(time.ticks_us()-st,buffer)
#     
# if 1:
#     from machine import Pin,  UART
#     uart = UART(2, baudrate=115200, bits=8, parity=None, stop=1)  # 设置串口号2和波特率
# #     uart = UART(2, 115200, rx=2, tx=1, bits=8, parity=None, stop=1)  # 设置串口号2和波特率
#     data='as5600:0'
#     st=time.ticks_us()
#     uart.read(1024)
#     mode_name,arg=data.split(':')
#     uart.write(str(4087).encode('utf-8'))
#     print(time.ticks_us()-st,'uart')
    

neo = neopixel(pin_id='A0', num=240, timing=[350, 800, 700, 600])
# as5600=encoder_as5600(sda_id='D3',scl_id='D1')
as5600 = encoder_as5600()
tcrt = TCRT5000(pin_id='C3')

mode_dict={
            1: ['EARTH',1,blue],#显示地球
            2: ['COUNT',20,yellow],#倒计时设置（滚轮设置好然后确认）
            3: ['CUBE',3,white],#显示立方体
            4: ['TICK',10,red],#显示秒表（停表）
            5: ['WATCH',5,purple],#显示现实时间
            6: ['FACE',6,orange],#显示面图像
            7: ['SNAKE',7,green],#显示贪吃蛇图像
            8: ['ALL',8,cyan]#外圈显示所有灯
        }

if __name__ == "__main__":
    while 1:
        if mode == 0:  # 实时计算
            if not have_cul:
                neo.clear()
                gc.collect()
                print('进入UI...', gc.mem_free() / 1024)
                from xy2num import *
                from word3x5 import *
                from show_UI import *
                ui = UI(as5600, neo, mode_dict,speed=-0.04, word_height=6, word_weight=4)
                have_cul = True
                gc.collect()
                print('进入完毕', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='button', arg=45): pass  # 8挡位模式
            else:
                now_mode = ui.UI_fun(neo, word3x5, tcrt, xy2num)  # 运行相关函数
                if mode != now_mode:  # 有改变
                    print('退出UI...', gc.mem_free() / 1024)
                    mode = mode_dict[now_mode][1]
                    have_cul = False
                    del ui, UI, xy2num, word3x5
                    gc.collect()
                    print('退出完毕', gc.mem_free() / 1024)
                time.sleep_ms(10)

        elif mode == 1:  # 先算后播放
            if not have_cul:
                neo.clear()
                gc.collect()
                print('显示地球...', gc.mem_free() / 1024)
                from earth_img import *
                from show_earth import *
                have_cul = True
                old_flame_index = flame_index = 0
                tcrt.gate=0.3
                gc.collect()
                print('进入完毕', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='speed', arg=16): pass  # 恒速旋转10度每秒
            else:
                flame_index = as5600.read_flame(flame=earth_num)[0]
                if old_flame_index != flame_index:
                    flame = noon[flame_index]
                    now_mode = earth_fun(flame, neo, tcrt, mode=mode)
                    old_flame_index = flame_index
                    if mode != now_mode:  # 有改变
                        print('退出地球...', gc.mem_free() / 1024)
                        have_cul = False
                        mode = now_mode
                        tcrt.gate=0.8
                        del noon, earth_fun
                        gc.collect()
                        print('退出地球显示模式', gc.mem_free() / 1024)

        elif 20 <= mode <= 21:  # 实时计算
            if not have_cul:
                neo.clear()
                gc.collect()
                print('进入倒计时...', gc.mem_free() / 1024)
                from show_clock import *
                clock = CLOCK()
                have_cul = True
                gc.collect()
                print('进入完毕', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='button', arg=8): pass  # 角度模式
#                 while motor_fun(as5600, run_mode='stop', arg=0): pass  #
            else:
                now_mode = clock.set_clock_fun(as5600, neo, tcrt, mode)
                if mode != now_mode:  # 有改变
                    mode = now_mode
                    if mode ==0 or mode==22:#如果不是回主界面，就不需要清除
                        have_cul = False
                        print('退出倒计时...', gc.mem_free() / 1024)
                        del hour, minute, second, scale_minute, scale_hour, clock, CLOCK
                        gc.collect()
                        print('退出完毕', gc.mem_free() / 1024)
                # 倒计时，分两个阶段，第一下旋钮选择倒计时长，第二下开始，自第二下后必须长按才能回到mode0

        elif mode == 22:  # 闹铃模式（倒计时时间到）
            if not have_cul:
                neo.clear()
                gc.collect()
                have_cul = True
                print('发送音乐')
                from song import *
                while motor_fun(as5600, run_mode='music', arg=90): pass  # 音乐模式（
            else:
                have_cul = False
                mode = 0
                print('开始播放音乐...')
                music_show(neo)
#                 time.sleep(15)  # 等待闹钟响完就行
                del notes_list,song,notes_bar,color_bar,music_show
                gc.collect()
                print('音乐播放完毕')

        elif 10 <= mode <= 12:  # 秒表三循环
            if not have_cul:
                gc.collect()
                print('进入秒表...', gc.mem_free() / 1024)
                from show_clock import *
                clock = CLOCK()
                have_cul = True
                gc.collect()
                print('进入秒表', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='angle', arg=90): pass  # 角度模式
#                 while motor_fun(as5600, run_mode='stop', arg=0): pass  # 停止模式
            else:
                now_mode = clock.stop_watch_fun(neo, tcrt, mode)  # 实时计算
                if mode != now_mode:  # 有改变
                    mode = now_mode
                    if mode ==0:#如果不是回主界面，就不需要清除
                        print('退出秒表...', gc.mem_free() / 1024)
                        have_cul = False
                        del hour, minute, second, scale_minute, scale_hour, clock, CLOCK
                        gc.collect()
                        print('退出秒表完毕', gc.mem_free() / 1024)

        elif mode == 3:  # 显示立方体
            if not have_cul:  # 先算后播放
                neo.clear()
                gc.collect()
                cube_num=16
                
                print('显示立方体...', gc.mem_free() / 1024)
                from show_cube import *
                tcrt.gate=0.3
                randt = R_and_T(cube)  # 旋转和平移矩阵
                cube_p = make_cube_p(cube, flame_num=cube_num)  # 计算极坐标下的点
                alpha = 0
                alpha_num = 10
                have_cul = True
                start_cube = time.ticks_us()
                old_flame_index = flame_index = 0
                gc.collect()
                print('显示立方体', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='speed', arg=20): pass
            else:
                if time.ticks_us() - start_cube > 2000000:  # 2秒后计算下一帧
                    gc.collect()
                    cube_r = randt.Ro(alpha=0, gamma=alpha, beta=0)  # 旋转立方体
                    cube_ = []  # 记录xyz
                    for cu in range(cube_num):  # 将矩阵xyz三维换回8个点的xyz
                        cube_.append([cube_r.matrix[0][cu], cube_r.matrix[1][cu], cube_r.matrix[2][cu]])
                    cube_p = make_cube_p(cube_, flame_num=cube_num)  # 计算极坐标下的点
#                     alpha = (alpha + 2 * pi / alpha_num) % (2 * pi)
                    start_cube = time.ticks_us()
                flame_index = as5600.read_flame(flame=cube_num)[0]
                if flame_index != old_flame_index:
                    now_mode = cube_fun(cube_p, flame_index, neo, tcrt, mode,flame_num=cube_num)  # 显示在屏幕上
                    old_flame_index = flame_index
                    if mode != now_mode:  # 有改变
                        have_cul = False
                        mode = now_mode
                        tcrt.gate=0.3
                        print('退出立方体...', gc.mem_free() / 1024)
                        del randt, cube_p, cube_fun, cube_r, start_cube, cube, make_cube_p, Matrix, R_and_T, find_nearest_element, xy2num, cube_num
                        gc.collect()
                        print('退出完毕...', gc.mem_free() / 1024)


        elif mode == 5:
            if not have_cul:
                neo.clear()
                gc.collect()
                print('显示现实时钟...', gc.mem_free() / 1024)
                from show_clock import *
                clock = CLOCK()
                have_cul = True
                gc.collect()
                print('显示现实时钟...', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='angle', arg=90): pass  # 角度模式
            else:
                now_mode = clock.real_clock(neo, tcrt, word3x5, mode)
                if mode != now_mode:  # 有改变
                    print('退出现实时钟', gc.mem_free() / 1024)
                    have_cul = False
                    mode = now_mode
                    del hour, minute, second, scale_minute, scale_hour, clock, CLOCK
                    gc.collect()
                    print('退出现实时钟', gc.mem_free() / 1024)

        elif mode == 6:
            if not have_cul:
                neo.clear()
                gc.collect()
                print('显示2D动画...', gc.mem_free() / 1024)
                from show_face import *
                from face_img import *
                face_player = FACE_player(face, yellow)
                have_cul = True
                gc.collect()
                print('显示2D动画', gc.mem_free() / 1024)
                old_flame_id=flame_id=90
            else:
                flame_id = face_player.flame['id']  # 需要到达的角度（0-360）
                if flame_id!=old_flame_id:
                    while motor_fun(as5600, run_mode='angle', arg=flame_id): pass  # 角度模式
                    old_flame_id=flame_id
                now_mode = face_player.face_fun(neo, tcrt, mode=mode)
                if mode != now_mode:  # 有改变
                    have_cul = False
                    mode = now_mode
                    print('退出2D动画...', gc.mem_free() / 1024)
                    del face_player, face, FACE_player
                    gc.collect()
                    print('退出完毕', gc.mem_free() / 1024)

        elif mode == 61:  # 显示球形动画
            if not have_cul:  # 第一次
                neo.clear()
                gc.collect()
                print('显示3D球形动画...', gc.mem_free() / 1024)
                from show_ball import *
                from ball_img import *
                from edge_12 import *
                have_cul = True
                gc.collect()
                print('显示3D球形动画', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='speed', arg=20): pass  # 速度模式
            else:
                now_mode = ball_fun(neo, tcrt, edge=edge_12,flame=ball[as5600.read_flame(flame=ball_num)[0]], mode=mode)
                if mode != now_mode:  # 有改变
                    have_cul = False
                    mode = now_mode
                    print('退出3D球形动画...', gc.mem_free() / 1024)
                    del ball_fun, ball,edge_12
                    gc.collect()
                    print('退出完毕', gc.mem_free() / 1024)

        elif mode == 62:
            if not have_cul:
                neo.clear()
                gc.collect()
                print('显示3D球形动画...', gc.mem_free() / 1024)
                from show_face3D import *
                from face3D_img import *
                face_player = FACE3D_player(face3D, yellow)
                have_cul = True
                flame_index = old_flame_index=0
                gc.collect()
                print('显示3D球形动画', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='speed', arg=20): pass  # 速度模式
            else:
                flame_index = as5600.read_flame(flame=flame_num)[0]
                if flame_index != old_flame_index:
                    old_flame_index=flame_index
                    now_mode = face_player.face_fun(flame_index,neo, tcrt, mode=mode)
                    if mode != now_mode:  # 有改变
                        have_cul = False
                        mode = now_mode
                        print('退出3D球形动画...', gc.mem_free() / 1024)
                        del face_player, face3D, FACE3D_player,big_edge
                        gc.collect()
                        print('退出完毕', gc.mem_free() / 1024)

        elif mode == 7:  # 贪吃蛇模式
            if not have_cul:  # 第一次
                neo.clear()
                gc.collect()
                while motor_fun(as5600, run_mode='speed', arg=20): pass  # 速度模式
                print('进入贪吃蛇模式...', gc.mem_free() / 1024)
                from show_PC_pic import *
                have_cul = True
                rev_time=0#转多几圈再获取下一帧
                ball = as5600.get_pc_uart()
                tcrt.gate=0.3
                print('贪吃蛇:',ball)
                gc.collect()
                print('进入完毕', gc.mem_free() / 1024)
            else:
                val, rev = as5600.read_flame(flame=flame_num)
                if rev:  # 不为0说明跨圈了，可以获取下一帧了
                    rev_time+=1
                    if rev_time>30:
                        print('获取新的贪吃蛇...')
                        try:
                            ball = as5600.get_pc_uart()
                            print('ball:',ball)
                            rev_time=0
                        except:
                            print('获取失败')
                            pass
                flame = ball[val]
                print('flame>>',flame)
                now_mode = show_pc_fun(flame, neo, tcrt, mode=mode)
                if mode != now_mode:  # 有改变
                    have_cul = False
                    mode = now_mode
                    tcrt.gate=0.8
                    print('退出贪吃蛇模式...', gc.mem_free() / 1024)
                    del show_pc_fun
                    gc.collect()
                    print('退出完毕', gc.mem_free() / 1024)
        
        elif mode == 8:  # 先算后播放
            if not have_cul:
                neo.clear()
                gc.collect()
                print('显示全条纹...', gc.mem_free() / 1024)
                from edge_12 import *
                from edge_9 import *
                from show_all import show_all
                old_flame_index=flame_index=0          
                have_cul = True
                tcrt.gate=0.3
                gc.collect()
                print('进入完毕', gc.mem_free() / 1024)
                while motor_fun(as5600, run_mode='speed', arg=40): pass  # 恒速旋转10度每秒
            else:
                flame_index = as5600.read_flame(flame=flame_num)[0]
                if old_flame_index != flame_index:
#                     flame = noon[flame_index]
#                     now_mode = earth_fun(flame, neo, tcrt, mode=mode)
                    old_flame_index = flame_index
                    if flame_index>=flame_num//2:
                        now_mode=show_all(edge_12, neo, tcrt,color=[1,0,0], mode=mode)
                    else:
                        now_mode=show_all(edge_9, neo, tcrt,color=[0,0,1], mode=mode)
                        
                    old_flame_index=flame_index
                    if mode != now_mode:  # 有改变
                        print('退出全条纹...', gc.mem_free() / 1024)
                        have_cul = False
                        tcrt.gate=0.8
                        mode = now_mode
                        del edge_12,edge_9, show_all
                        gc.collect()
                        print('退出全条纹显示模式', gc.mem_free() / 1024)

        else:
            print('没有该模式的入口！')
            mode = 0  # 回到主界面













