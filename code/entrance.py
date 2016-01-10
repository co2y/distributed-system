import threading
import time
import socket
from message import Message
import pickle


class Entrance(threading.Thread):

    def __init__(self, ip, port, parking_num):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.parkingNum = parking_num
        self.nodeInfo = []
        self.state = 'RELEASED'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.localTimeStamp = 0
        self.handleList = []
        self.waitingCarNum = 0
        self.replyNum = 0
        self.applyThread = ''

    def run(self):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)
        while True:
            conn, address = self.sock.accept()
            raw_message = conn.recv(1024)
            message = pickle.loads(raw_message)
            if message.type == 'REPLY':
                self.replyNum -= 1
                print('入口节点:', self.port - 33000, '\t',
                      '收到自己发出申请的回复请求,还差{number}个'.format(number=self.replyNum))
                self.localTimeStamp += 1
            elif message.type == 'APPLY':
                self.handleList.append(message)
                if self.handleList and self.state != 'HELD':
                    self.send_reply()
                self.localTimeStamp = max(
                    self.localTimeStamp, message.timestamp) + 1
            elif message.type == 'MINUS':
                self.parkingNum -= 1
                print('入口节点:', self.port - 33000, '收到车位数减1消息',
                      '\t', '调整空闲车位数:', self.parkingNum)
                self.localTimeStamp = max(
                    self.localTimeStamp, message.timestamp) + 1
            elif message.type == 'PLUS':
                self.parkingNum += 1
                print('入口节点:', self.port - 33000, '收到车位数加1消息',
                      '\t', '调整空闲车位数:', self.parkingNum)
                self.localTimeStamp = max(
                    self.localTimeStamp, message.timestamp) + 1
            elif message.type == 'IN':
                if self.state == 'RELEASED':
                    self.state = 'WANTED'
                    print('入口节点:', self.port - 33000, '有车请求进入,向其它入口发出申请')
                    self.applyThread = threading.Thread(target=self.apply)
                    self.applyThread.start()
                elif self.state == 'WANTED':
                    print('入口节点:', self.port - 33000, '\t', '有车在之前发出了请求,请排队')
                    self.waitingCarNum += 1
                elif self.state == '':
                    print()

    def apply(self):
        apply_message = Message(
            'APPLY', self.localTimeStamp, self.ip, self.port)
        self.handleList.append(apply_message)
        self.replyNum = self.get_entrance_num() - 1
        self.send_msg_all(apply_message)
        while self.replyNum > 0:
            time.sleep(0.5)
        self.state = 'HELD'
        self.replyNum = self.get_entrance_num() - 1
        while self.parkingNum <= 0:
            print('入口节点:', self.port - 33000, '没有车位了,请等待,每秒检查一次')
            time.sleep(1)
        self.parkingNum -= 1
        print('入口节点:', self.port - 33000, '有空闲车位,车辆进入,需要2s',
              '\t', '空闲车位数:', self.parkingNum)
        minus_message = Message(
            'MINUS', self.localTimeStamp, self.ip, self.port)
        time.sleep(2)
        self.send_msg_all(minus_message)
        if self.handleList:
            self.send_reply_all()
        self.localTimeStamp += 1
        if self.waitingCarNum:
            self.state = 'WANTED'
            self.waitingCarNum -= 1
            self.apply()
        else:
            self.state = "RELEASED"

    def get_entrance_num(self):
        count = 0
        for node in self.nodeInfo:
            if node.name == 'entrance':
                count += 1
        return count

    def send_msg_all(self, message):
        for node in self.nodeInfo:
            if node.port != self.port:
                message.timestamp = self.localTimeStamp
                client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((node.ip, node.port))
                client_socket.send(pickle.dumps(message))
                client_socket.close()

    def send_reply(self):
        message = Message('REPLY', self.localTimeStamp, self.ip, self.port)
        min_index = self.get_min_index()
        min_message = self.handleList[min_index]
        self.handleList.remove(min_message)
        if min_message.port != self.port:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((min_message.ip, min_message.port))
            client.send(pickle.dumps(message))
            client.close()

    def get_min_index(self):
        min_index = 0
        timestamp_list = []
        port_list = []
        for each_message in self.handleList:
            timestamp_list.append(each_message.timestamp)
            port_list.append(each_message.port)
        min_timestamp = timestamp_list[0]
        length = len(timestamp_list)
        for i in range(length):
            if timestamp_list[i] == timestamp_list[min_index]:
                if port_list[i] < port_list[min_index]:
                    min_index = i
            elif timestamp_list[i] < min_timestamp:
                min_timestamp = timestamp_list[i]
                min_index = i
        return min_index

    def send_reply_all(self):
        send_message = Message(
            'REPLY', self.localTimeStamp, self.ip, self.port)
        length = len(self.handleList)
        while length > 0:
            each_message = self.handleList[0]
            self.handleList.remove(each_message)
            length -= 1
            if each_message.port != self.port:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((each_message.ip, each_message.port))
                client.send(pickle.dumps(send_message))
                client.close()

    def get_all_info(self, node_info):
        self.nodeInfo = node_info
