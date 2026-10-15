# Um agente precisa pegar um pacote e entregá-lo no destino, num grid quadrado com obstáculos (intransponíveis) e pedágios (ação custa +2)
# Convenção de posições: tupla (linha, coluna), com (0, 0) no canto

from aigyminsper.search.graph import State

class GridWorld(State):

    # o mundo fixo durante a busca e compartilhado por todos os estados
    # começa vazio porque o Python executa este trecho ao carregar o arquivo, antes de o usuário escolher a dimensão
    # os valores reais são definidos em mundo.py

    DIMENSAO = 0
    OBSTACULOS = set() # set de tuplas (linha, coluna)
    PEDAGIOS = set() # set de tuplas (linha, coluna)
    META = None  # tupla (linha, coluna) do destino da entrega

    # estado o que muda quando o agente executa uma ação.
    def __init__(self, op, pos_agente, pos_pacote, com_agente, custo=1, custo_acumulado=0):
        super().__init__(op)  # guarda a ação que gerou este estado
        self.pos_agente = pos_agente # tupla (linha, coluna)
        self.pos_pacote = pos_pacote # tupla; quando com_agente, acompanha o agente
        self.com_agente = com_agente # True se o pacote está na mão do agente
        self.custo = custo  # custo da ação que gerou este estado
        self.custo_acumulado = custo_acumulado

    def custo_da_acao(self):

        if self.pos_agente in GridWorld.PEDAGIOS:
            return 1 + 2   # custo pedagio: custo = custo + 2

        return 1 # custo padrão

    def successors(self):
        successors = []

        MOVIMENTOS = { # ações/movimento:
            "cima": (-1, 0),
            "baixo": (1, 0),
            "esquerda": (0, -1),
            "direita": (0, 1),
        }
        
        linha, coluna = self.pos_agente
        custo = self.custo_da_acao()
        acumulado = self.custo_acumulado + custo

        # movimentos
        for acao, (dl, dc) in MOVIMENTOS.items():
            nova_pos = (linha + dl, coluna + dc)

            dentro = (0 <= nova_pos[0] < GridWorld.DIMENSAO
                      and 0 <= nova_pos[1] < GridWorld.DIMENSAO)

            if not dentro or nova_pos in GridWorld.OBSTACULOS: # impede que saia do grid e vá para obstaculos
                continue

            # se o pacote está com o agente, ele anda junto
            nova_pos_pacote = nova_pos if self.com_agente else self.pos_pacote
            successors.append(
                GridWorld(acao, nova_pos, nova_pos_pacote, self.com_agente, custo, acumulado))

        # pegar pacote: só se ele está na mesma célula e ainda não está na mão
        if not self.com_agente and self.pos_agente == self.pos_pacote:
            successors.append(
                GridWorld("pegar", self.pos_agente, self.pos_pacote, True, custo, acumulado))

        # entregar pacote: solta na célula atual
        if self.com_agente:
            successors.append(
                GridWorld("entregar", self.pos_agente, self.pos_agente, False, custo, acumulado))

        return successors

    def is_goal(self):
        # pacote no destino e já entregue
        if self.pos_pacote == GridWorld.META and not self.com_agente:
            return True
        else:
            return False

    def description(self):
        return "Entregador em grid quadrado com obstáculos e pedágios"

    def cost(self):
        return self.custo

    def h(self):

        # Heurística admissível para o A*:
        # distância de Manhattan que ainda falta andar + ações pegar/entregar que ainda faltam
        # Ignora obstáculos e pedágios, e toda ação custa  no mínimo 1, então nao superestima o custo real

        if self.com_agente:
            return manhattan(self.pos_agente, GridWorld.META) + 1  # + entregar
        return (manhattan(self.pos_agente, self.pos_pacote)
                + manhattan(self.pos_pacote, GridWorld.META)
                + 2)  # + pegar + entregar

    def env(self):
        # Representação usada pela busca para identificar estados repetidos
        # Segue a convenção do template da disciplina: estado + "#" + custo
        return (str(self.pos_agente) + "#" + str(self.pos_pacote) + "#"
                + str(self.com_agente) + "#" + str(self.custo_acumulado))

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])