import heapq
import networkx as nx
import matplotlib.pyplot as plt
import ipaddress
import time

class Dispositivo:
    def __init__(self, nome, ip, tipo, gateway=None, subnet=None):
        """
        :param nome: Nome do dispositivo (ex: 'h1', 'r1', 's1').
        :param ip: Endereço IP com máscara (ex: '172.16.1.1/24').
        :param tipo: Tipo do dispositivo ('host', 'roteador', 'comutador').
        """
        self.nome = nome
        self.ip = ip.split('/')[0]  # Remove a máscara
        self.subnet = subnet or self.calcular_subnet(ip)
        self.tipo = tipo
        self.gateway = gateway
        self.vizinhos = {}  # {Dispositivo: (custo, enlace, capacidade, justificativa)}
        self.tabela_roteamento = {} if self.tipo == 'roteador' else None

    def calcular_subnet(self, ip):
        """Calcula a sub-rede a partir do IP com máscara."""
        try:
            rede = ipaddress.ip_network(ip, strict=False)
            return str(rede)
        except ValueError:
            return None
    
    def adicionar_vizinho(self, vizinho, custo=1, enlace='fibra', capacidade='1Gbps', justificativa='Backbone'):
        self.vizinhos[vizinho] = (custo, enlace, capacidade, justificativa)
    
    def __str__(self):
        return f"{self.tipo.capitalize()} {self.nome} (IP: {self.ip}, Subnet: {self.subnet})"

class Rede:
    def __init__(self):
        self.dispositivos = []
        self.enlaces = []  # Lista para armazenar informações de enlaces

    def adicionar_dispositivo(self, dispositivo):
        self.dispositivos.append(dispositivo)
    
    def adicionar_link(self, dispositivo1, dispositivo2, custo=1, enlace='fibra', capacidade='1Gbps', justificativa='Backbone'):
        dispositivo1.adicionar_vizinho(dispositivo2, custo, enlace, capacidade, justificativa)
        dispositivo2.adicionar_vizinho(dispositivo1, custo, enlace, capacidade, justificativa)
        self.enlaces.append((dispositivo1, dispositivo2, custo, enlace, capacidade, justificativa))

    def bfs(self, dispositivo_inicial):
        distancias = {d: float('inf') for d in self.dispositivos}
        distancias[dispositivo_inicial] = 0
        anteriores = {d: None for d in self.dispositivos}

        counter = 0
        fila = [(0, counter, dispositivo_inicial)]

        while fila:
            distancia_atual, _, dispositivo_atual = heapq.heappop(fila)
            if distancia_atual > distancias[dispositivo_atual]:
                continue
            for vizinho, (custo, _, _, _) in dispositivo_atual.vizinhos.items():
                distancia_vizinho = distancia_atual + custo
                if distancia_vizinho < distancias[vizinho]:
                    distancias[vizinho] = distancia_vizinho
                    anteriores[vizinho] = dispositivo_atual
                    counter += 1
                    heapq.heappush(fila, (distancia_vizinho, counter, vizinho))
        return anteriores

    def ping(self, ip_origem, ip_destino):
        origem = next((d for d in self.dispositivos if d.ip == ip_origem), None)
        destino = next((d for d in self.dispositivos if d.ip == ip_destino), None)
        
        if not origem or not destino:
            return 'Dispositivo de origem ou destino não encontrado.'
        
        inicio = time.time()
        anteriores = self.bfs(origem)
        fim = time.time()
        
        if anteriores[destino] is None:
            return 'Destino inalcançável!'
        else:
            tempo_resposta = (fim - inicio) * 1000
            return f'Ping de {ip_origem} para {ip_destino} realizado com sucesso! Tempo: {tempo_resposta:.2f}ms'

    def traceroute(self, ip_origem, ip_destino):
        origem = next((d for d in self.dispositivos if d.ip == ip_origem), None)
        destino = next((d for d in self.dispositivos if d.ip == ip_destino), None)
        
        if not origem or not destino:
            return 'Dispositivo de origem ou destino não encontrado.'
        
        anteriores = self.bfs(origem)
        caminho = []
        passo_atual = destino
        
        while passo_atual is not None:
            caminho.append(f'{passo_atual.nome} ({passo_atual.ip})')
            passo_atual = anteriores[passo_atual]
        
        caminho.reverse()
        return ' -> '.join(caminho) if caminho else 'Destino inalcançável!'

    def plotar_rede(self):
        """Plota a topologia da rede usando matplotlib e networkx."""
        G = nx.Graph()
        
        # Adiciona dispositivos ao grafo
        for dispositivo in self.dispositivos:
            G.add_node(dispositivo.nome, ip=dispositivo.ip, tipo=dispositivo.tipo, subnet=dispositivo.subnet)
            
        # Adiciona links ao grafo
        for dispositivo in self.dispositivos:
            for vizinho, (custo, enlace, capacidade, justificativa) in dispositivo.vizinhos.items():
                G.add_edge(
                dispositivo.nome, 
                vizinho.nome, 
                weight=custo,
                enlace=enlace,
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
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_shape=shape, node_color=cores[i], node_size=500)
        
        # Desenha arestas
        cores_enlace = {
        'fibra': 'red',
        'par trançado': 'green',
        'coaxial': 'blue',
        'sem fio': 'purple'
        }
        
        for edge in G.edges(data=True):
            tipo = edge[2]['enlace']
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(edge[0], edge[1])], 
                edge_color=cores_enlace.get(tipo, 'gray'), 
                width=2.0
            )
        
        nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray')
        
        # Desenha rótulos
        labels = {node: f"{node}\nIP: {data['ip']}\nSubnet: {data['subnet']}" for node, data in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=4, font_color='black')
        
        # Desenha pesos das arestas
        edge_labels = {}
        for edge in G.edges(data=True):
            tipo = edge[2]['enlace']
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
    
    def mostrar_tabelas_roteamento(self):
        for dispositivo in self.dispositivos:
            if dispositivo.tipo == 'roteador':
                anteriores = self.bfs(dispositivo)
                for dest in self.dispositivos:
                    if dest.subnet and dest != dispositivo:
                        passo_atual = dest
                        while anteriores[passo_atual] != dispositivo and anteriores[passo_atual] is not None:
                            passo_atual = anteriores[passo_atual]
                        if anteriores[passo_atual] == dispositivo:
                            dispositivo.tabela_roteamento[dest.subnet] = passo_atual.ip
                
                print(f"\n=== Tabela de Roteamento - {dispositivo.nome} ({dispositivo.ip}) ===")
                print("Destino (Subnet)        | Próximo Salto")
                print("----------------------------------------")
                for subnet, next_hop in dispositivo.tabela_roteamento.items():
                    print(f"{subnet:22} | {next_hop}")
