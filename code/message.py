class Message:

    def __init__(self, message_type, timestamp, ip, port):
        self.type = message_type
        self.timestamp = timestamp
        self.ip = ip
        self.port = port
