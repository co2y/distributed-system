import threading
import socket
from message import Message
import pickle


class Exit(threading.Thread):

    def __init__(self, ip, port, parking_num):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.parkingNum = parking_num
        self.nodeInfo = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.localTimeStamp = 0
        self.carNum = 0

    def run(self):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)
        while True:
            conn, address = self.sock.accept()
            raw_message = conn.recv(1024)
            message = pickle.loads(raw_message)
            if message.type == 'MINUS':
                self.parkingNum -= 1
                self.carNum += 1
                print('出口节点:', self.port - 33000, '收到车位数减1消息',
                      '\t', '调整空闲车位数:', self.parkingNum)
                self.localTimeStamp = max(
                    self.localTimeStamp, message.timestamp) + 1
            elif message.type == 'OUT':
                self.out()
                self.localTimeStamp += 1
            elif message.type == 'PLUS':
                self.parkingNum += 1
                self.carNum -= 1
                print('出口节点:', self.port - 33000, '收到车位数加1消息',
                      '\t', '调整空闲车位数:', self.parkingNum)
                self.localTimeStamp = max(
                    self.localTimeStamp, message.timestamp) + 1

    def out(self):
        if self.carNum <= 0:
            print('停车场内没有车')
        else:
            self.carNum -= 1
            message = Message('PLUS', self.localTimeStamp, self.ip, self.port)
            print('出口节点:', self.port - 33000, '车辆驶出',
                  '\t', '空闲车位数:', self.parkingNum)
            self.send_msg_all(message)
            self.parkingNum += 1

    def send_msg_all(self, message):
        for node in self.nodeInfo:
            if node.port != self.port:
                message.timestamp = self.localTimeStamp
                client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((node.ip, node.port))
                client_socket.send(pickle.dumps(message))
                client_socket.close()

    def get_all_info(self, node_info):
        self.nodeInfo = node_info
