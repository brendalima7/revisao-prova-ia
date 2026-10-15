# Criação do mundo: aleatória (para a interface) ou fixa (para exemplos/testes).

import random
from gridworld import GridWorld

def configurar_mundo(mundo):
    """Copia as informações fixas do mundo para os atributos da classe GridWorld."""
    GridWorld.DIMENSAO = mundo["dimensao"]
    GridWorld.OBSTACULOS = set(mundo["obstaculos"])
    GridWorld.PEDAGIOS = set(mundo["pedagios"])
    GridWorld.META = mundo["meta"]


def gerar_mundo(dimensao, semente=None):
    # Gera um mundo aleatório n x n.

    # Sorteia a quantidade, posição de obstáculos, pedágios, e as posições do agente, do pacote e do destino. Agente, pacote e destino
    # sempre caem em células diferentes e livres de obstáculo. Pedágios podem coincidir com agente/pacote/destino (o enunciado não proíbe).
    
    if dimensao < 2:
        raise ValueError("A dimensão mínima é 2.")

    rng = random.Random(semente)
    celulas = [(l, c) for l in range(dimensao) for c in range(dimensao)]
    rng.shuffle(celulas)

    # as 3 primeiras células embaralhadas viram agente, pacote e destino
    agente, pacote, meta = celulas[0], celulas[1], celulas[2]
    livres = celulas[3:]

    # até 30% das células como obstáculo (quantidade também é aleatória)
    max_obst = int(0.30 * dimensao * dimensao)
    qtd_obst = rng.randint(0, min(max_obst, len(livres)))
    obstaculos = set(livres[:qtd_obst])

    # até 20% das células como pedágio, entre as que não são obstáculo
    candidatas_pedagio = [c for c in celulas if c not in obstaculos]
    max_ped = int(0.20 * dimensao * dimensao)
    qtd_ped = rng.randint(0, min(max_ped, len(candidatas_pedagio)))
    pedagios = set(rng.sample(candidatas_pedagio, qtd_ped))

    return {
        "dimensao": dimensao,
        "obstaculos": obstaculos,
        "pedagios": pedagios,
        "agente": agente,
        "pacote": pacote,
        "meta": meta,
    }

def mundo_da_prova():
    """Exemplo 3x3 usado na resposta da prova."""
    return {
        "dimensao": 3,
        "obstaculos": {(1, 1)},
        "pedagios": {(0, 1)},
        "agente": (0, 0),
        "pacote": (0, 2),
        "meta": (2, 1),
    }

def desenhar_texto(mundo, caminho=()):
    """
    Desenho do mundo no terminal.
    A agente | P pacote | X destino | # obstáculo | $ pedágio | * caminho
    """
    n = mundo["dimensao"]
    caminho = set(caminho)
    linhas = []
    for l in range(n):
        linha = []
        for c in range(n):
            pos = (l, c)
            if pos == mundo["agente"]:
                s = "A"
            elif pos == mundo["pacote"]:
                s = "P"
            elif pos == mundo["meta"]:
                s = "X"
            elif pos in mundo["obstaculos"]:
                s = "#"
            elif pos in caminho:
                s = "*"
            elif pos in mundo["pedagios"]:
                s = "$"
            else:
                s = "."
            linha.append(s)
        linhas.append(" ".join(linha))
    return "\n".join(linhas)
