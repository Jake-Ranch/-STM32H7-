def motor_fun(as5600,run_mode,arg):#1.run_mode运行模式（角度模式/恒速模式/音乐/停止）2.arg参数（角度/速度/list格式的乐谱）
    text='{}:{}'.format(run_mode,arg)
    print('开始发送电机配置')
    data=as5600.uart_send_motor(text=text)  # 发送数据
    print('发送串口给电机：',text,'收到ESP反馈：',data)
    if data==text:
#         as5600.clear_uart_buffer()#清理干净UART残留数据
        return False#成功返回模式名字，说明ESP接收成功
    else:
        return True