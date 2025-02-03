from topologia import Dispositivo, Rede
import re

def validar_ip(ip):
    """Valida se o IP está no formato correto (com ou sem máscara)."""
    padrao = r"^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$"
    return re.match(padrao, ip) is not None

def listar_dispositivos(rede):
    """Lista todos os dispositivos na rede."""
    print("\nDispositivos na rede:")
    for i, dispositivo in enumerate(rede.dispositivos):
        tipo = dispositivo.tipo.capitalize()
        print(f"{i}: {dispositivo.nome} ({tipo}) - IP: {dispositivo.ip}, Subnet: {dispositivo.subnet}")

def adicionar_host(rede):
    """Adiciona um host à rede via CLI."""
    nome = input("Nome do host (ex: h1): ").strip()
    ip = input("IP do host com máscara (ex: 172.16.1.1/24): ").strip()
    gateway = input("IP do gateway (ex: 172.16.1.66): ").strip()
    
    # Valida o IP do host e do gateway
    if not validar_ip(ip):
        print("Erro: IP do host inválido!")
        return
    if not validar_ip(gateway):
        print("Erro: IP do gateway inválido!")
        return
    
    # Verifica se o gateway existe
    gateway_existe = any(d.ip == gateway for d in rede.dispositivos)
    if not gateway_existe:
        print("Erro: Gateway não encontrado na rede!")
        return
    
    host = Dispositivo(nome, ip, 'host', gateway)
    rede.adicionar_dispositivo(host)
    print(f"Host {nome} adicionado com sucesso!")

def adicionar_link(rede):
    """Adiciona um link entre dois dispositivos."""
    listar_dispositivos(rede)
    
    try:
        idx1 = int(input("Índice do primeiro dispositivo: "))
        idx2 = int(input("Índice do segundo dispositivo: "))
        custo = int(input("Custo do link (padrão=1): ") or 1)
        enlace = input("Tipo de enlace (fibra, par trançado, coaxial, sem fio): ").strip()
        capacidade = input("Capacidade do enlace (ex: 1Gbps): ").strip()
        justificativa = input("Justificativa do enlace (ex: Conexão backbone): ").strip()
    except ValueError:
        print("Entrada inválida!")
        return
    
    if idx1 < 0 or idx2 < 0 or idx1 >= len(rede.dispositivos) or idx2 >= len(rede.dispositivos):
        print("Índice inválido!")
        return
    
    dispositivo1 = rede.dispositivos[idx1]
    dispositivo2 = rede.dispositivos[idx2]
    rede.adicionar_link(dispositivo1, dispositivo2, custo, enlace, capacidade, justificativa)
    print(f"Link entre {dispositivo1.nome} e {dispositivo2.nome} adicionado!")

def executar_ping(rede):
    """Executa o comando ping entre dois IPs."""
    ip_origem = input("IP de origem (ex: 172.16.1.1): ").strip()
    ip_destino = input("IP de destino (ex: 172.16.2.33): ").strip()
    print(rede.ping(ip_origem, ip_destino))

def executar_traceroute(rede):
    """Executa o comando traceroute entre dois IPs."""
    ip_origem = input("IP de origem (ex: 172.16.1.1): ").strip()
    ip_destino = input("IP de destino (ex: 172.16.2.33): ").strip()
    print(rede.traceroute(ip_origem, ip_destino))

def menu():
    """Exibe o menu principal."""
    print("\n=== Menu ===")
    print("1. Adicionar Host")
    print("2. Adicionar Link")
    print("3. Executar Ping")
    print("4. Executar Traceroute")
    print("5. Plotar Rede")
    print("6. Listar Dispositivos")
    print("7. Mostrar Tabelas de Roteamento")
    print("8. Sair")

def main():
    rede = Rede()
    
    # Dispositivos iniciais
    c1 = Dispositivo('c1', '172.16.0.1/24', 'roteador', subnet='172.16.0.0/24')
    a1 = Dispositivo('a1', '172.16.1.1/24', 'comutador', subnet='172.16.1.0/24')
    a2 = Dispositivo('a2', '172.16.2.1/24', 'comutador', subnet='172.16.2.0/24')
    e1 = Dispositivo('e1', '172.16.1.66/24', 'comutador', subnet='172.16.1.0/24')
    e2 = Dispositivo('e2', '172.16.1.70/24', 'comutador', subnet='172.16.1.0/24')
    e3 = Dispositivo('e3', '172.16.2.66/24', 'comutador', subnet='172.16.2.0/24')
    e4 = Dispositivo('e4', '172.16.2.70/24', 'comutador', subnet='172.16.2.0/24')
    
    hosts = [
        Dispositivo(f'h{i}', f'172.16.{i//24+1}.{i%24+2}/24', 'host', gateway=f'172.16.{i//24+1}.66', subnet=f'172.16.{i//24+1}.0/24')
        for i in range(48)
    ]
    
    # Adiciona todos os dispositivos à rede
    for dispositivo in [c1, a1, a2, e1, e2, e3, e4] + hosts:
        rede.adicionar_dispositivo(dispositivo)
    
    # Conexões (topologia em árvore)
    rede.adicionar_link(c1, a1, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    rede.adicionar_link(c1, a2, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    
    rede.adicionar_link(a1, e1, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a1, e2, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a2, e3, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a2, e4, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    
    for i, host in enumerate(hosts):
        edge_switch = e1 if i < 12 else e2 if i < 24 else e3 if i < 36 else e4
        rede.adicionar_link(edge_switch, host, enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    
    # Constrói tabelas de roteamento
    rede.mostrar_tabelas_roteamento()
    
    while True:
        menu()
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            adicionar_host(rede)
        elif escolha == '2':
            adicionar_link(rede)
        elif escolha == '3':
            executar_ping(rede)
        elif escolha == '4':
            executar_traceroute(rede)
        elif escolha == '5':
            rede.plotar_rede()
        elif escolha == '6':
            listar_dispositivos(rede)
        elif escolha == '7':
            rede.mostrar_tabelas_roteamento()
        elif escolha == '8':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()


'''
Construção de uma topologia menor

rede = Rede()
    
    # Dispositivos iniciais
    c1 = Dispositivo('c1', '172.16.0.1/24', 'roteador', subnet='172.16.0.0/24')
    a1 = Dispositivo('a1', '172.16.1.1/24', 'comutador', subnet='172.16.1.0/24')
    a2 = Dispositivo('a2', '172.16.2.1/24', 'comutador', subnet='172.16.2.0/24')
    e1 = Dispositivo('e1', '172.16.1.66/24', 'comutador', subnet='172.16.1.0/24')
    e2 = Dispositivo('e2', '172.16.1.70/24', 'comutador', subnet='172.16.1.0/24')
    e3 = Dispositivo('e3', '172.16.2.66/24', 'comutador', subnet='172.16.2.0/24')
    e4 = Dispositivo('e4', '172.16.2.70/24', 'comutador', subnet='172.16.2.0/24')
    
    hosts = [
        Dispositivo('h1', '172.16.1.2/24', 'host', gateway='172.16.1.66', subnet='172.16.1.0/24'),
        Dispositivo('h2', '172.16.1.3/24', 'host', gateway='172.16.1.66', subnet='172.16.1.0/24'),
        Dispositivo('h3', '172.16.1.34/24', 'host', gateway='172.16.1.70', subnet='172.16.1.0/24'),
        Dispositivo('h4', '172.16.1.35/24', 'host', gateway='172.16.1.70', subnet='172.16.1.0/24'),
        Dispositivo('h5', '172.16.2.2/24', 'host', gateway='172.16.2.66', subnet='172.16.2.0/24'),
        Dispositivo('h6', '172.16.2.3/24', 'host', gateway='172.16.2.66', subnet='172.16.2.0/24'),
        Dispositivo('h7', '172.16.2.34/24', 'host', gateway='172.16.2.70', subnet='172.16.2.0/24'),
        Dispositivo('h8', '172.16.2.35/24', 'host', gateway='172.16.2.70', subnet='172.16.2.0/24')
    ]
    
    # Adiciona todos os dispositivos à rede
    for dispositivo in [c1, a1, a2, e1, e2, e3, e4] + hosts:
        rede.adicionar_dispositivo(dispositivo)
    
    # Conexões (topologia em árvore)
    rede.adicionar_link(c1, a1, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    rede.adicionar_link(c1, a2, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    
    rede.adicionar_link(a1, e1, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a1, e2, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a2, e3, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a2, e4, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    
    rede.adicionar_link(e1, hosts[0], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e1, hosts[1], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e2, hosts[2], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e2, hosts[3], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e3, hosts[4], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e3, hosts[5], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e4, hosts[6], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')
    rede.adicionar_link(e4, hosts[7], enlace='par trançado', capacidade='100Mbps', justificativa='Conexão de borda')

'''