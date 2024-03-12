import socket
import pickle
import argparse
import time

class Client:
    def __init__(self, hosts, ports):
        self.hosts = hosts
        self.ports = ports

    def inputRequest(self):
        flag = True
        while flag:
            try:
                n = int(input("Escolha o servidor que irá receber a requisição?\n"))
                self.establishConnection(n)
                requestType = input("1 para \"ler\" ou 2 para \"atualizar/adicionar\" \n")
                start = 0
                if requestType == '1':
                    key = input("Digite a chave do valor \n")
                    start = time.time()
                    self.readDataRequest(key)
                elif requestType == '2':
                    key = input("Digite a chave: \n")
                    value = input("Digite o valor: \n")
                    start = time.time()
                    self.updateDataRequest(key, value)
                else:
                    continue
                self.receiveData()
                end = time.time()
                print("Tempo decorrido: " + str(end - start))
                self.closeConnection()
                flag = input("Quer continuar? s ou n \n")
                if flag == "n":
                    flag = False
            except:
                self.closeConnection()
                print("Reiniciando requisição, erro ocorreu durante a execução")

    def readDataRequest(self, key):
        request = pickle.dumps(key)
        self.client.send(request)

    def updateDataRequest(self, key, value):
        request = pickle.dumps((key, value))
        self.client.send(request)

    def establishConnection(self, i):
        self.client = socket.socket()
        self.client.connect((self.hosts[i], self.ports[i]))
        self.client.send(pickle.dumps("Client"))

    def receiveData(self):
        data = pickle.loads(self.client.recv(1024 * 100))
        if len(data) == 1:
            print("Dados recebidos: \n", data)
        else:
            print("Dados recebidos com conflito:\n", data)
        return data

    def closeConnection(self):
        self.client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', nargs="+", help='Hosts', default=["localhost", "localhost", "localhost"])
    parser.add_argument('--ports', nargs="+", help="Ports", default=[9990, 9980, 9999])
    args = parser.parse_args()
    hosts, ports = args.hosts, args.ports
    ports = [int(element) for element in ports]
    client = Client(hosts, ports)
    client.inputRequest()
