import server
import client
import threading

def test_case(client1, dummy_client):
    print("\n----Caso de teste 1----")
    client1.establishConnection(0)
    threading.Event().wait(1)
    print("\nConexão estabelecida com o servidor 0\n")
    dummy_client.establishConnection(1)
    threading.Event().wait(1)
    client1.updateDataRequest("Chave-0", "Valor-0")
    print("Enviando uma requisição de atualização\n")
    data = client1.receiveData()
    client1.closeConnection()
    
    print("\nConexão estabelecida com o servidor 2\n")
    client1.establishConnection(2)
    threading.Event().wait(1)
    client1.updateDataRequest("Chave-1", "Valor-1")
    print("Enviando uma requisição de atualização\n")
    data = client1.receiveData()
    client1.closeConnection()
    dummy_client.closeConnection()

    client1.establishConnection(2)
    threading.Event().wait(1)
    print("\nConexão estabelecida com o servidor 2\n")
    client1.readDataRequest("Chave-1")
    print("Enviando uma requisição de leitura para ler a Key \"Chave-1\n")
    data = client1.receiveData()
    client1.closeConnection()
    
    
    

if __name__ == '__main__':
    hosts, ports = ["localhost", "localhost", "localhost", "localhost", "localhost"], [9920, 9950, 9990, 9980, 9999]
    
    server1 = server.Server(hosts, ports, 0, 3)
    server2 = server.Server(hosts, ports, 1, 3)
    server3 = server.Server(hosts, ports, 2, 3)
    
    threading.Thread(target=server1.startListening, args=[], daemon=True).start()
    threading.Thread(target=server2.startListening, args=[], daemon=True).start()
    threading.Thread(target=server3.startListening, args=[], daemon=True).start()
    
    client1 = client.Client(hosts, ports)
    
    dummy_client0 = client.Client(hosts, ports)
    dummy_client1 = client.Client(hosts, ports)
    dummy_client2 = client.Client(hosts, ports)
    
    test_case(client1, dummy_client0)
    
