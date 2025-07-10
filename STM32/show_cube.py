from cube_img import *


def cube_fun(cube_p,i,neo,tcrt,mode=3,flame_num=24): 
    flame = cube_p[i]
    back_flame = cube_p[(i + flame_num // 2) % flame_num]
    for j in flame:  # 取出该帧的所有点（边缘）
        neo.change(j[0], j[1:])
    for j in back_flame:  # 取出该帧的所有点（边缘）
        neo.change(j[0], j[1:])
    neo.write()
    for j in flame:  # 取出该帧的所有点（边缘）
        neo.change(j[0], [0,0,0])
    for j in back_flame:  # 取出该帧的所有点（边缘）
        neo.change(j[0], [0,0,0])
    neo.write()
    
    have_down, long_push = tcrt.have()
    if have_down:  # 长按退出
        return 0
    else:
        return mode  # 留在当前状态




if __name__ == "__main__":
    from myneopixel import *
    from read_as5600_uart import *
#     from read_as5600 import *
    from read_TCRT import *
    import gc,time

    neo=neopixel(pin_id='A0',num=240,timing=[350, 800, 700, 600])
    # as5600=encoder_as5600(sda_id='D3',scl_id='D1')
    as5600 = encoder_as5600(round_gate=0.5)
    
    tcrt = TCRT5000(pin_id='C3')
    flame_num=36
    mode=3


    if 0:
        def cul_cube(alpha_num = 100):
            randt = R_and_T(cube)  # 旋转和平移矩阵
            cube_p_list = []
            alpha = 0
            for i in range(alpha_num):  # 转多少次(cube_p_lilst的长度)
                cube_r = randt.Ro(alpha=alpha, gamma=0, beta=0)  # 旋转立方体
                cube_ = []#记录xyz
                for cu in range(cube_num):# 将矩阵xyz三维换回8个点的xyz
                    cube_.append([cube_r.matrix[0][cu], cube_r.matrix[1][cu], cube_r.matrix[2][cu]])
                cube_p = make_cube_p(cube_, flame_num=flame_num)  # 计算极坐标下的点
                cube_p_list.append(cube_p)
                alpha = (alpha + 2 * pi / alpha_num)
            gc.collect()
            return cube_p_list
        neo.clear()
        alpha_num = 10
        cube_p_list=cul_cube(alpha_num = alpha_num)
        st=time.time()
        cube_id=0
        cube_p = cube_p_list[cube_id]
        while cube_id<alpha_num:#不能超出范围
            if time.time()-st>1:
                cube_p=cube_p_list[cube_id]
                cube_id += 1
                st = time.time()
            cube_fun(cube_p,as5600,neo,tcrt,mode)#显示在屏幕上
            
    else:
        alpha_num=100
        randt = R_and_T(cube)  # 旋转和平移矩阵
        alpha = 0
        
        cube_r = randt.Ro(alpha=alpha, gamma=0, beta=0)  # 旋转立方体
        cube_ = []#记录xyz
        for cu in range(cube_num):# 将矩阵xyz三维换回8个点的xyz
            cube_.append([cube_r.matrix[0][cu], cube_r.matrix[1][cu], cube_r.matrix[2][cu]])
        cube_p = make_cube_p(cube_, flame_num=36)  # 计算极坐标下的点
        
        old_flame_id=flame_id=0
        start_cube=time.ticks_us()
        while 1:#不能超出范围
            if time.ticks_us()-start_cube>1000000:
                cube_r = randt.Ro(alpha=alpha, gamma=0, beta=0)  # 旋转立方体
                cube_ = []#记录xyz
                for cu in range(cube_num):# 将矩阵xyz三维换回8个点的xyz
                    cube_.append([cube_r.matrix[0][cu], cube_r.matrix[1][cu], cube_r.matrix[2][cu]])
                cube_p = make_cube_p(cube_, flame_num=36)  # 计算极坐标下的点
                alpha = (alpha + 2 * pi / alpha_num)


            
            flame_id=as5600.read_flame(flame=36)[0]
            if flame_id!=old_flame_id:
                print(flame_id)
                cube_fun(cube_p,flame_id,neo,tcrt,mode)#显示在屏幕上
                old_flame_id=flame_id






