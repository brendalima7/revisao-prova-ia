# Exemplos de execução no terminal
# saídas ficam salvas em exemplos/

from busca import resolver
from mundo import desenhar_texto, gerar_mundo, mundo_da_prova

def rodar(titulo, mundo):
    linhas = [f"=== {titulo} ===",
              "Legenda: A agente | P pacote | X destino | # obstáculo | $ pedágio | * caminho",
              "",
              desenhar_texto(mundo),
              ""]
    r = resolver(mundo)
    if not r["solucao"]:
        linhas.append("Não existe solução para este problema.")
    else:
        caminho = [e.pos_agente for e in r["estados"]]
        linhas += ["Plano: " + " ; ".join(r["plano"]),
                   f"Ações: {len(r['plano'])} | Custo: {r['custo']}",
                   "",
                   desenhar_texto(mundo, caminho)]
    texto = "\n".join(linhas)
    print(texto + "\n")
    return texto

if __name__ == "__main__":
    import os
    os.makedirs("exemplos", exist_ok=True)

    casos = [
        ("01_mundo_da_prova_3x3", mundo_da_prova()),
        ("02_aleatorio_10x10", gerar_mundo(10, semente=1)),
        ("03_aleatorio_15x15", gerar_mundo(15, semente=4)),
        # mundo montado à mão sem solução: pacote cercado por obstáculos
        ("04_sem_solucao_5x5", {
            "dimensao": 5,
            "obstaculos": {(1, 2), (2, 1), (2, 3), (3, 2)},
            "pedagios": {(0, 1)},
            "agente": (0, 0),
            "pacote": (2, 2),
            "meta": (4, 4),
        }),
    ]
    for nome, mundo in casos:
        texto = rodar(nome, mundo)
        with open(os.path.join("exemplos", nome + ".txt"), "w", encoding="utf-8") as f:
            f.write(texto + "\n")
