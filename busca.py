#Resolução do problema com o A* da aigyminsper (AEstrela) e detecção de mundo sem solução


from collections import deque
from aigyminsper.search.search_algorithms import AEstrela
from gridworld import GridWorld
from mundo import configurar_mundo


def alcancavel(origem, destino):
    
    # Busca em largura simples só para saber se dá para ir de origem até destino desviando dos obstáculos (ignora custos).
    
    fila = deque([origem])
    visitados = {origem}
    while fila:
        atual = fila.popleft()
        if atual == destino:
            return True
        for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            viz = (atual[0] + dl, atual[1] + dc)
            if (0 <= viz[0] < GridWorld.DIMENSAO and 0 <= viz[1] < GridWorld.DIMENSAO
                    and viz not in GridWorld.OBSTACULOS and viz not in visitados):
                visitados.add(viz)
                fila.append(viz)
    return False


def existe_solucao(mundo):
    #Só existe plano se o agente alcança o pacote E o pacote alcança o destino
    return (alcancavel(mundo["agente"], mundo["pacote"])
            and alcancavel(mundo["pacote"], mundo["meta"]))


def resolver(mundo):
    """
    Devolve um dicionário com o resultado:
      - "solucao": False se não existe plano
      - "plano": lista de ações
      - "custo": custo total do plano
      - "estados": estados do início ao fim (para animar na interface)
    """
    configurar_mundo(mundo)

    # Verificação necessária: como o env() inclui o custo acumulado, num mundo
    # sem solução o AEstrela continuaria gerando caminhos cada vez mais caros
    # e nunca terminaria.
    if not existe_solucao(mundo):
        return {"solucao": False}

    estado_inicial = GridWorld("", mundo["agente"], mundo["pacote"], False)
    algoritmo = AEstrela()
    # "general": não adiciona nó cujo env() já foi gerado
    resultado = algoritmo.search(estado_inicial, pruning="general")

    if resultado is None:
        return {"solucao": False}

    # reconstrói a sequência de estados percorrendo os pais
    estados = []
    no = resultado
    while no is not None:
        estados.append(no.state)
        no = no.father_node
    estados.reverse()

    return {
        "solucao": True,
        "plano": [e.operator for e in estados[1:]],
        "custo": resultado.g,
        "estados": estados,
    }