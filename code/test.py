import socket
from message import Message
import pickle

ip = '127.0.0.1'
port = 33062
base_port = 33000


def car_send_msg(msg_list):
    length = len(msg_list)
    for i in range(length):
        info = msg_list[i].split(',')
        node_port = int(info[0]) + base_port
        node_msg = info[1]
        msg = Message(node_msg, -1, ip, port)
        car = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        car.connect(('127.0.0.1', node_port))
        car.send(pickle.dumps(msg))
        car.close()


if __name__ == '__main__':
    while 1:
        try:
            event = input(
                "请输入事件,格式[1-3,IN 4-6,OUT],可输入多个事件,表示同时发生,例如:1,IN 2,IN 4,OUT 未做异常处理,请按格式输入\n")
            event_list = event.split(' ')
            car_send_msg(event_list)
        except Exception as e:
            print("指令有误")
            continue
