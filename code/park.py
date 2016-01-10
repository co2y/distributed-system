from entrance import Entrance
from exit import Exit
from nodeinfo import NodeInfo
import sys


class Park:

    def __init__(self, entrance_num, exit_num, parking_num):
        self.entranceNum = entrance_num
        self.exitNum = exit_num
        self.totalNum = entrance_num + exit_num
        self.parkingNum = parking_num
        self.port = 33000
        self.nodes = []
        self.nodeInfo = []

    def start(self):
        for i in range(self.entranceNum):
            entrance_node = Entrance(
                "127.0.0.1", self.port + 1, self.parkingNum)
            info = NodeInfo("127.0.0.1", self.port + 1, "entrance")
            self.port += 1
            self.nodes.append(entrance_node)
            self.nodeInfo.append(info)
            print('入口节点:', self.port - 33000, '\t', '空闲车位数:', self.parkingNum)

        for i in range(self.exitNum):
            exit_node = Exit("127.0.0.1", self.port + 1, self.parkingNum)
            info = NodeInfo("127.0.0.1", self.port + 1, "exit")
            self.port += 1
            self.nodes.append(exit_node)
            self.nodeInfo.append(info)
            print('出口节点:', self.port - 33000, '\t', '空闲车位数:', self.parkingNum)

        for i in range(self.totalNum):
            self.nodes[i].get_all_info(self.nodeInfo)

        for i in range(self.totalNum):
            self.nodes[i].start()

    def add_entrance(self):
        pass

    def add_exit(self):
        pass


if __name__ == '__main__':
    # a,b,c三个参数分别代表入口数、出口数以及空闲车位数
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    c = int(sys.argv[3])
    p = Park(a, b, c)
    print('欢迎来到停车场,请从test端按要求输入测试指令')
    print('编号1-{x}代表入口，{y}-{z}代表出口'.format(x=a, y=a + 1, z=a + b))
    p.start()
