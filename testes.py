"""
Testes da solução.  Rode:  python testes.py

Compara o custo do plano do A* com o de uma busca de custo uniforme
exata (Dijkstra) em centenas de mundos aleatórios, e verifica a
detecção de mundos sem solução.
"""

import heapq
import itertools

from busca import resolver
from gridworld import GridWorld
from mundo import configurar_mundo, gerar_mundo, mundo_da_prova


def situacao(estado):
    """O que identifica o estado no mundo (sem custos)."""
    return (estado.pos_agente, estado.pos_pacote, estado.com_agente)


def custo_otimo_referencia(mundo):
    """Custo ótimo calculado por busca de custo uniforme (sem heurística)."""
    configurar_mundo(mundo)
    inicial = GridWorld("", mundo["agente"], mundo["pacote"], False)
    desempate = itertools.count()
    melhor = {situacao(inicial): 0}
    fila = [(0, next(desempate), inicial)]
    while fila:
        g, _, estado = heapq.heappop(fila)
        if estado.is_goal():
            return g
        if g > melhor[situacao(estado)]:
            continue
        for s in estado.successors():
            ng = g + s.cost()
            if ng < melhor.get(situacao(s), float("inf")):
                melhor[situacao(s)] = ng
                heapq.heappush(fila, (ng, next(desempate), s))
    return None


def simular(mundo, plano):
    """Executa o plano a partir do estado inicial e devolve o estado final."""
    configurar_mundo(mundo)
    estado = GridWorld("", mundo["agente"], mundo["pacote"], False)
    for acao in plano:
        proximos = [s for s in estado.successors() if s.operator == acao]
        assert proximos, f"ação inválida no plano: {acao}"
        estado = proximos[0]
    return estado


def teste_mundo_da_prova():
    r = resolver(mundo_da_prova())
    assert r["solucao"]
    assert r["custo"] == 9
    assert r["plano"][-1] == "entregar"


def teste_sem_solucao():
    mundo = {
        "dimensao": 5,
        "obstaculos": {(1, 2), (2, 1), (2, 3), (3, 2)},
        "pedagios": set(),
        "agente": (0, 0),
        "pacote": (2, 2),
        "meta": (4, 4),
    }
    assert resolver(mundo)["solucao"] is False


def teste_mundos_aleatorios(quantidade=500):
    sem_solucao = 0
    for semente in range(quantidade):
        n = 2 + semente % 14
        mundo = gerar_mundo(n, semente=semente)
        r = resolver(mundo)
        referencia = custo_otimo_referencia(mundo)
        if not r["solucao"]:
            assert referencia is None, f"semente {semente}: tinha solução"
            sem_solucao += 1
            continue
        assert r["custo"] == referencia, (
            f"semente {semente}: A* custo {r['custo']}, ótimo {referencia}")
        assert simular(mundo, r["plano"]).is_goal()
    return sem_solucao


if __name__ == "__main__":
    teste_mundo_da_prova()
    print("ok - mundo da prova")
    teste_sem_solucao()
    print("ok - mundo sem solução")
    s = teste_mundos_aleatorios()
    print(f"ok - 500 mundos aleatórios com custo ótimo ({s} sem solução detectados)")
