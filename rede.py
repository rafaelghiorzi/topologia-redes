import matplotlib.pyplot as plt
import networkx as nx

class Dispositivo:
    def __init__(self, nome, ip, tipo, gateway=None, subnet=None):
        """
        :param nome: Nome do dispositivo (ex: 'h1', 'r1', 's1').
        :param ip: Endereço IP com máscara (ex: '172.16.1.1/24').
        :param tipo: Tipo do dispositivo ('host', 'roteador', 'comutador').
        :param gateway: Gateway padrão (apenas para hosts).
        :param subnet: Sub-rede associada (ex: '172.16.1.0/24').
        """
        self.nome = nome
        self.ip = ip.split('/')[0]  # Remove a máscara para armazenar apenas o IP
        self.subnet = subnet or self.calcular_subnet(ip)
        self.tipo = tipo
        self.gateway = gateway
        self.vizinhos = {}  # {Dispositivo: (custo, tipo_enlace, capacidade, justificativa)}
        
        if self.tipo == 'roteador':
            self.tabela_roteamento = {}  # {destino_subnet: próximo_salto_ip}
        if self.tipo == 'comutador':
            self.tabela_mac = {}  # {mac_address: porta}

    def calcular_subnet(self, ip):
        """Calcula a sub-rede a partir do IP com máscara (ex: '172.16.1.1/24' -> '172.16.1.0/24')."""
        if '/' in ip:
            ip_part, mask = ip.split('/')
            octetos = ip_part.split('.')
            octetos[-1] = '0'  # Assume sub-rede classe C (simplificação)
            return '.'.join(octetos) + f'/{mask}'
        return None
    
    def adicionar_vizinho(self, vizinho, custo=1, tipo_enlace='fibra', capacidade='1Gbps', justificativa='Conexão backbone'):
        """Adiciona um vizinho ao dispositivo."""
        self.vizinhos[vizinho] = (custo, tipo_enlace, capacidade, justificativa)

    def __str__(self):
        return f"{self.tipo.capitalize()} {self.nome} (IP: {self.ip}, Subnet: {self.subnet})"

class Rede:
    def __init__(self):
        self.dispositivos = []
    
    def adicionar_dispositivo(self, dispositivo):
        self.dispositivos.append(dispositivo)
    
    def adicionar_link(self, dispositivo1, dispositivo2, custo=1, tipo_enlace='fibra', capacidade='1Gbps', justificativa='Conexão backbone'):
        dispositivo1.adicionar_vizinho(dispositivo2, custo, tipo_enlace, capacidade, justificativa)
        dispositivo2.adicionar_vizinho(dispositivo1, custo, tipo_enlace, capacidade, justificativa)
    
    def dijkstra(self, dispositivo_inicial):
        """Implementa o algoritmo de Dijkstra para encontrar o caminho mais curto."""
        distancias = {dispositivo: float('inf') for dispositivo in self.dispositivos}
        anteriores = {dispositivo: None for dispositivo in self.dispositivos}
        distancias[dispositivo_inicial] = 0
        nao_visitados = set(self.dispositivos)
        
        while nao_visitados:
            atual = min(nao_visitados, key=lambda d: distancias[d])
            nao_visitados.remove(atual)
            
            for vizinho, (custo, *_) in atual.vizinhos.items():  # Extrai apenas o custo da tupla
                alternativa = distancias[atual] + custo
                if alternativa < distancias[vizinho]:
                    distancias[vizinho] = alternativa
                    anteriores[vizinho] = atual
        return anteriores
    
    def construir_tabelas_roteamento(self):
        """Constrói tabelas de roteamento para todos os roteadores."""
        for dispositivo in self.dispositivos:
            if dispositivo.tipo == 'roteador':
                anteriores = self.dijkstra(dispositivo)
                for destino in self.dispositivos:
                    if destino != dispositivo and anteriores[destino]:
                        caminho = []
                        passo_atual = destino
                        while anteriores[passo_atual] != dispositivo:
                            passo_atual = anteriores[passo_atual]
                        proximo_salto = passo_atual
                        dispositivo.tabela_roteamento[destino.ip] = proximo_salto.ip
                        
    def mostrar_tabelas_roteamento(self):
        """Exibe as tabelas de roteamento de todos os roteadores."""
        for dispositivo in self.dispositivos:
            if dispositivo.tipo == 'roteador':
                print(f"\n=== Tabela de Roteamento - {dispositivo.nome} ({dispositivo.ip}) ===")
                print("Destino (Subnet)        | Próximo Salto")
                print("----------------------------------------")
                for subnet, next_hop in dispositivo.tabela_roteamento.items():
                    print(f"{subnet:22} | {next_hop}")
    
    def ping(self, ip_origem, ip_destino):
        """Simula o comando ping, verificando se há um caminho entre dois dispositivos."""
        origem = next((d for d in self.dispositivos if d.ip == ip_origem), None)
        destino = next((d for d in self.dispositivos if d.ip == ip_destino), None)
        
        if not origem or not destino:
            return "Dispositivo de origem ou destino não encontrado."
        
        anteriores = self.dijkstra(origem)
        if anteriores[destino] is not None:
            return f"Ping de {ip_origem} para {ip_destino} bem-sucedido."
        else:
            return f"Ping de {ip_origem} para {ip_destino} falhou. Destino inalcançável."
    
    def traceroute(self, ip_origem, ip_destino):
        """Simula o comando traceroute, mostrando o caminho entre dois dispositivos."""
        origem = next((d for d in self.dispositivos if d.ip == ip_origem), None)
        destino = next((d for d in self.dispositivos if d.ip == ip_destino), None)
        
        if not origem or not destino:
            return "Dispositivo de origem ou destino não encontrado."
        
        anteriores = self.dijkstra(origem)
        caminho = []
        passo_atual = destino
        
        while passo_atual is not None:
            caminho.append(f"{passo_atual.nome} ({passo_atual.ip})")  # Nome e IP
            passo_atual = anteriores[passo_atual]
        
        caminho.reverse()
        return " -> ".join(caminho) if caminho else "Destino inalcançável."
    
    def plotar_rede(self):
        """Plota a topologia da rede usando matplotlib e networkx."""
        G = nx.Graph()
        
        # Adiciona dispositivos ao grafo
        for dispositivo in self.dispositivos:
            G.add_node(dispositivo.nome, ip=dispositivo.ip, tipo=dispositivo.tipo, subnet=dispositivo.subnet)
            
        # Adiciona links ao grafo
        for dispositivo in self.dispositivos:
            for vizinho, (custo, tipo_enlace, capacidade, justificativa) in dispositivo.vizinhos.items():
                G.add_edge(
                dispositivo.nome, 
                vizinho.nome, 
                weight=custo,
                tipo_enlace=tipo_enlace,
                capacidade=capacidade,
                justificativa=justificativa
                )
        
        # Define cores e formas para os nós
        cores = []
        formas = []
        for node in G.nodes(data=True):
            if node[1]['tipo'] == 'roteador':
                cores.append('lightblue')
                formas.append('s')  # Quadrado para roteadores
            elif node[1]['tipo'] == 'comutador':
                cores.append('orange')
                formas.append('D')  # Diamante para comutadores
            else:
                cores.append('lightgreen')
                formas.append('o')  # Círculo para hosts
        
        # Desenha o grafo
        pos = nx.spring_layout(G)
        plt.figure(figsize=(14, 10))
        
        # Desenha nós
        for i, (node, shape) in enumerate(zip(G.nodes(), formas)):
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_shape=shape, node_color=cores[i], node_size=2500)
        
        # Desenha arestas
        cores_enlace = {
        'fibra': 'red',
        'par trançado': 'green',
        'coaxial': 'blue',
        'sem fio': 'purple'
        }
        
        for edge in G.edges(data=True):
            tipo = edge[2]['tipo_enlace']
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(edge[0], edge[1])], 
                edge_color=cores_enlace.get(tipo, 'gray'), 
                width=2.0
            )
        
        nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray')
        
        # Desenha rótulos
        labels = {node: f"{node}\nIP: {data['ip']}\nSubnet: {data['subnet']}" for node, data in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black')
        
        # Desenha pesos das arestas
        edge_labels = {}
        for edge in G.edges(data=True):
            tipo = edge[2]['tipo_enlace']
            capacidade = edge[2]['capacidade']
            justificativa = edge[2]['justificativa']
            edge_labels[(edge[0], edge[1])] = f"{tipo}\n{capacidade}\n({justificativa})"
    
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, font_color='darkred')
        
        # Legenda
        legend_labels = {
            'Roteador': 'lightblue',
            'Comutador': 'orange',
            'Host': 'lightgreen',
            'Fibra': 'red',
            'Par Trançado': 'green',
            'Coaxial': 'blue',
            'Sem Fio': 'purple'
        }
        for label, color in legend_labels.items():
            plt.plot([], [], color=color, label=label)        

        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.title("Topologia da Rede")
        plt.tight_layout()
        plt.show()

def construir_tabelas_roteamento(self):
    """Constrói tabelas de roteamento baseadas em sub-redes usando Dijkstra."""
    for dispositivo in self.dispositivos:
        if dispositivo.tipo == 'roteador':
            anteriores = self.dijkstra(dispositivo)
            subnets_unicas = set()
            
            # Coleta todas as sub-redes
            for dest in self.dispositivos:
                if dest.subnet and dest != dispositivo:
                    subnets_unicas.add(dest.subnet)
            
            # Preenche a tabela de roteamento
            for subnet in subnets_unicas:
                # Encontra o próximo salto para a sub-rede
                for dest in self.dispositivos:
                    if dest.subnet == subnet:
                        passo_atual = dest
                        while anteriores[passo_atual] != dispositivo and anteriores[passo_atual] is not None:
                            passo_atual = anteriores[passo_atual]
                        if anteriores[passo_atual] == dispositivo:
                            dispositivo.tabela_roteamento[subnet] = passo_atual.ip
                        break

def mostrar_tabelas_roteamento(self):
    """Exibe as tabelas de roteamento de todos os roteadores."""
    for dispositivo in self.dispositivos:
        if dispositivo.tipo == 'roteador':
            self.construir_tabelas_roteamento(dispositivo)
    
    for dispositivo in self.dispositivos:
        if dispositivo.tipo == 'roteador':
            print(f"\n=== Tabela de Roteamento - {dispositivo.nome} ({dispositivo.ip}) ===")
            print("Destino (Subnet)        | Próximo Salto")
            print("----------------------------------------")
            for subnet, next_hop in dispositivo.tabela_roteamento.items():
                print(f"{subnet:22} | {next_hop}")
                
                
"""
# Exemplo de uso
if __name__ == "__main__":
    # Criação da rede
    rede = Rede()
    
    # Dispositivos
    c1 = Dispositivo('c1', '172.16.0.1', 'roteador')
    a1 = Dispositivo('a1', '172.16.0.2', 'comutador')
    a2 = Dispositivo('a2', '172.16.0.6', 'comutador')
    e1 = Dispositivo('e1', '172.16.1.66', 'comutador')
    e2 = Dispositivo('e2', '172.16.1.70', 'comutador')
    e3 = Dispositivo('e3', '172.16.2.66', 'comutador')
    e4 = Dispositivo('e4', '172.16.2.70', 'comutador')
    
    hosts = [
        Dispositivo('h1', '172.16.1.1', 'host', '172.16.1.66'),
        Dispositivo('h2', '172.16.1.2', 'host', '172.16.1.66'),
        Dispositivo('h3', '172.16.1.33', 'host', '172.16.1.70'),
        Dispositivo('h4', '172.16.1.34', 'host', '172.16.1.70'),
        Dispositivo('h5', '172.16.2.1', 'host', '172.16.2.66'),
        Dispositivo('h6', '172.16.2.2', 'host', '172.16.2.66'),
        Dispositivo('h7', '172.16.2.33', 'host', '172.16.2.70'),
        Dispositivo('h8', '172.16.2.34', 'host', '172.16.2.70')
    ]
    
    # Adiciona todos os dispositivos à rede
    for dispositivo in [c1, a1, a2, e1, e2, e3, e4] + hosts:
        rede.adicionar_dispositivo(dispositivo)
    
    # Conexões
    rede.adicionar_link(c1, a1, 1)
    rede.adicionar_link(c1, a2, 1)
    rede.adicionar_link(a1, e1, 1)
    rede.adicionar_link(a1, e2, 1)
    rede.adicionar_link(a2, e3, 1)
    rede.adicionar_link(a2, e4, 1)
    
    for host in hosts[:2]:
        rede.adicionar_link(e1, host, 1)
    for host in hosts[2:4]:
        rede.adicionar_link(e2, host, 1)
    for host in hosts[4:6]:
        rede.adicionar_link(e3, host, 1)
    for host in hosts[6:]:
        rede.adicionar_link(e4, host, 1)
    
    # Constrói tabelas de roteamento
    rede.construir_tabelas_roteamento()
    
    # Plota a rede
    rede.plotar_rede()
    
    # Testes
    print(rede.traceroute('172.16.1.1', '172.16.2.33'))  # Traceroute entre h1 e h7
    print(rede.ping('172.16.1.1', '172.16.2.33'))  # Ping entre h1 e h7   
"""