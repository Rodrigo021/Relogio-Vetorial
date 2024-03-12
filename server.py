import socket
import pickle
import threading
import argparse

class Server:
    def __init__(self, hosts, ports, i, n):
        self.hosts, self.ports = hosts, ports
        self.index = i
        self.vectorClock = [0] * n
        self.data = {}
        self.socket = self.initiateServer(hosts[i], ports[i], n)

    def initiateServer(self, host, port, n):
        print("Bem vindo ao servidor: ", self.index)
        sock = socket.socket()
        print("Socket criado")
        sock.bind((host, port))
        sock.listen(n)
        return sock

    def acceptConnections(self):
        conn, address = self.socket.accept()
        connType = pickle.loads(conn.recv(1024 * 1000))
        connType = connType.split("-")
        connType, index = connType[0], connType[1] if len(connType) == 2 else None
        index = int(index) if index else None
        if connType == "Client":
            request = conn.recv(1024 * 1000)
            reply = self.requestHandler(request)
        else:
            data = pickle.loads(conn.recv(1024 * 100))
            if type(data) == tuple:
                request, receiveClock = data
                self.data[request[0]] = request[1]
                self.vectorClock[index] += 1
                reply = pickle.dumps((self.data, self.vectorClock))
            else:
                reply = pickle.dumps((self.data, self.vectorClock))
        conn.send(reply)
        conn.close()

    def startListening(self):
        flag = True
        while flag:
            try:
                self.acceptConnections()
            except:
                break

    def requestHandler(self, request):
        request = pickle.loads(request)
        if type(request) == tuple:
            reply = self.updateHandler(request)
        elif type(request) == str:
            reply = self.readHandler(request)
        return reply

    def synchronizeServers(self, request ,requestType):
        replyData = []
        for i in range(len(self.vectorClock)):
            if i == self.index:
                continue
            try:
                client = socket.socket()
                client.settimeout(0.05)
                client.connect((self.hosts[i], self.ports[i]))
                msg = "Server-" + str(self.index)
                client.send(pickle.dumps(msg))
                if requestType == "updateAdd":
                    client.send(pickle.dumps((request, self.vectorClock)))
                else:
                    client.send(pickle.dumps(self.vectorClock))
                data = pickle.loads(client.recv(1024 * 100))
                receiveData, receiveClock = data
                flag1, flag2 = True, True
                for j in range(len(self.vectorClock)):
                    if receiveClock[j] < self.vectorClock[j]:
                        flag1 = False
                    if receiveClock[j] > self.vectorClock[j]:
                        flag2 = False
                conflict = not flag1 and not flag2
                if conflict:
                    if requestType == "updateAdd":
                        replyData.append((receiveData, receiveClock))
                    else:
                        replyData.append((receiveData[request], receiveClock))
                else:
                    self.vectorClock = [max(receiveClock[j], self.vectorClock[j]) for j in range(len(receiveClock))]
                    if flag1:
                        self.data = receiveData
            except:
                break
            
        if requestType == "updateAdd":
            replyData.append((self.data, self.vectorClock))
        else:
            replyData.append((self.data[request], self.vectorClock))
        return replyData

    def updateHandler(self, request):
        self.data[request[0]] = request[1]
        self.vectorClock[self.index] += 1
        replyData = self.synchronizeServers(request, "updateAdd")
        reply = pickle.dumps(replyData)
        return reply

    def readHandler(self, request):
        replyData = self.synchronizeServers(request, "read")
        reply = pickle.dumps(replyData)
        return reply


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Replicated Database Vector Clock by Karandeep Parashar")
    parser.add_argument('--hosts', nargs="+", help='Hosts', default=["localhost", "localhost", "localhost"])
    parser.add_argument('--ports', nargs="+", help="Ports", default=[9990, 9980, 9999])
    args = parser.parse_args()
    hosts, ports = args.hosts, args.ports
    ports = [int(element) for element in ports]
    n = len(hosts)
    for i in range(1, n):
        server = Server(hosts, ports, i, n)
        serverThread = threading.Thread(target=server.startListening, args=[], daemon=True)
        serverThread.start()
    server = Server(hosts, ports, 0, n)
    server.startListening()
