from topologia import Dispositivo, Rede
from ipaddress import ip_network, ip_interface


def listar_dispositivos(rede):
    """Lista todos os dispositivos na rede."""
    print("\nDispositivos na rede:")
    for i, dispositivo in enumerate(rede.dispositivos):
        tipo = dispositivo.tipo.capitalize()
        print(f"{i}: {dispositivo.nome} ({tipo}) - IP: {dispositivo.ip}, Subnet: {dispositivo.subnet}")

# Executar ping funciona normalmente
def executar_ping(rede):
    """Executa o comando ping entre dois IPs."""
    ip_origem = input("IP de origem (ex: 172.16.1.1): ").strip()
    ip_destino = input("IP de destino (ex: 172.16.2.33): ").strip()
    print(rede.ping(ip_origem, ip_destino))

# Executar traceroute funciona normalmente
def executar_traceroute(rede):
    """Executa o comando traceroute entre dois IPs."""
    ip_origem = input("IP de origem (ex: 172.16.1.1): ").strip()
    ip_destino = input("IP de destino (ex: 172.16.2.33): ").strip()
    print(rede.traceroute(ip_origem, ip_destino))

# Menu do CLI
def menu():
    """Exibe o menu principal."""
    print("\n=== Menu ===")
    print("1. Adicionar Host")
    print("2. Executar Ping")
    print("3. Executar Traceroute")
    print("4. Plotar Rede")
    print("5. Listar Dispositivos")
    print("6. Mostrar Tabelas de Roteamento")
    print("7. Sair")

def main():
    rede = Rede()
    
    # 2^n - 2 >= hosts
    # Dispositivos iniciais
    c1 = Dispositivo('c1', '172.16.0.1/30', 'roteador')
    # /30 para aguentar no mínimo 4 subredes
    a1 = Dispositivo('a1', '172.16.0.2/30', 'roteador')
    a2 = Dispositivo('a2', '172.16.2.6/30', 'roteador')
    # /27 para aguentar no mínimo 24 hosts
    e1 = Dispositivo('e1', '172.16.1.1/27', 'comutador')
    e2 = Dispositivo('e2', '172.16.1.33/27', 'comutador')
    # /27 para aguentar no mínimo 15 hosts, /28 não aguentaria
    e3 = Dispositivo('e3', '172.16.2.1/27', 'comutador')
    e4 = Dispositivo('e4', '172.16.2.33/27', 'comutador')

    # Adiciona todos os dispositivos à rede
    for dispositivo in [c1, a1, a2, e1, e2, e3, e4]:
        rede.adicionar_dispositivo(dispositivo)
    # Conexões (topologia em árvore)
    
    # conexão entre c1 e a1 e a2
    rede.adicionar_link(c1, a1, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    rede.adicionar_link(c1, a2, enlace='fibra', capacidade='10Gbps', justificativa='Conexão backbone')
    # conexões de a1
    rede.adicionar_link(a1, e1, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a1, e2, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    # conexões de a2
    rede.adicionar_link(a2, e3, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    rede.adicionar_link(a2, e4, enlace='fibra', capacidade='1Gbps', justificativa='Conexão de agregação')
    
    """b) As subredes e1 e e2 devem ter capacidade para endereçar ao menos 24 hosts em cada uma.
    c) As subredes e3 e e4 devem ter capacidade para endereçar ao menos 15 hosts em cada uma"""

    # Adicionando 24 hosts em e1 e e2
    for i in range(2, 8):
        rede.adicionar_host(f'Host e1 {i}', f'172.16.1.{i}/27')
        
    for i in range(34, 41):
        rede.adicionar_host(f'Host e4 {i}', f'172.16.2.{i}/27')
        
    for i in range(2, 10):
        rede.adicionar_host(f'Host e3 {i}', f'172.16.2.{i}/27')    
        
    for i in range(34, 44):
        rede.adicionar_host(f'Host e2 {i}', f'172.16.1.{i}/27')
        
    
    # Constrói tabelas de roteamento
    rede.mostrar_tabelas_roteamento()
    
    while True:
        menu()
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            nome = input("Nome do host (ex: h1): ").strip()
            ip_str = input("IP do host com máscara (ex: 172.16.1.1/24): ").strip()
            rede.adicionar_host(nome, ip_str)
        elif escolha == '2':
            executar_ping(rede)
        elif escolha == '3':
            executar_traceroute(rede)
        elif escolha == '4':
            rede.plotar_rede()
        elif escolha == '5':
            listar_dispositivos(rede)
        elif escolha == '6':
            rede.mostrar_tabelas_roteamento()
        elif escolha == '7':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
