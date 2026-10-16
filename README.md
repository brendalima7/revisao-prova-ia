# Exercício de Revisão da Prova — Entregador no Grid

Implementação da solução proposta na Avaliação Intermediária de Inteligência
Artificial (Insper): um agente precisa **pegar um pacote e entregá-lo no destino**
com o **plano de menor custo**, num grid quadrado com obstáculos e células de pedágio.

## Como rodar

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

python main.py        # interface gráfica
python exemplos.py    # exemplos no terminal (salvos em exemplos/)
python testes.py      # testes de otimalidade e de mundos sem solução
```

Na interface: escolha a dimensão, clique em **Gerar mundo aleatório**, depois em
**Resolver (A\*)** e, se houver solução, em **Animar plano**.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `gridworld.py` | Modelo do problema: classe `GridWorld` (estado, sucessores, objetivo, custo, heurística) |
| `mundo.py` | Geração aleatória do mundo, mundo fixo da prova e desenho em texto |
| `busca.py` | Chamada do A\* da `aigyminsper`, detecção de mundo sem solução e montagem do resultado |
| `interface.py` | Interface gráfica (tkinter) |
| `main.py` | Ponto de entrada |
| `exemplos.py` / `exemplos/` | Exemplos de execução e suas saídas |
| `testes.py` | Testes automáticos |

## Modelagem

**Mundo (atributos de classe, fixos durante a busca):** `DIMENSAO`, `OBSTACULOS`
e `PEDAGIOS` (sets de tuplas `(linha, coluna)`) e `META` (tupla). Começam vazios e
são preenchidos por `configurar_mundo()` depois que o usuário escolhe a dimensão.

**Estado (atributos de instância):**

| Campo | Tipo | Significado |
|---|---|---|
| `pos_agente` | tupla `(linha, coluna)` | onde o agente está |
| `pos_pacote` | tupla `(linha, coluna)` | onde o pacote está (acompanha o agente quando está com ele) |
| `com_agente` | `bool` | se o pacote está na mão do agente |

Só as posições não bastam: com o agente e o pacote na mesma célula, o pacote pode
estar solto no chão ou na mão do agente, e os sucessores são diferentes.

Exemplo (mundo 3×3 da prova):
- estado inicial: `GridWorld("", (0, 0), (0, 2), False)`
- estado final: `GridWorld("entregar", (2, 1), (2, 1), False)` com `META = (2, 1)`

**Sucessores:** `cima`, `baixo`, `esquerda`, `direita` (se não sair do grid nem
entrar em obstáculo), `pegar` (se agente e pacote estão na mesma célula e o pacote
está solto) e `entregar` (se o pacote está na mão; ele fica na célula atual).
Movimentos que deixariam o agente parado não são gerados, porque repetem o mesmo
estado pagando custo e nunca fazem parte de um plano ótimo.

**Objetivo:** `pos_pacote == META` e o pacote não está mais na mão do agente.

**Custo:** toda ação custa 1; executada em célula de pedágio, custa 1 + 2 = 3.

## Algoritmo

Como os custos **não são uniformes** (pedágio), busca em largura e aprofundamento
iterativo não garantem o plano ótimo. Os algoritmos ótimos aqui são **custo uniforme**
e **A\* com heurística admissível**. Usamos A\*.

**Heurística:** distância de Manhattan que ainda falta percorrer, mais as ações de
pegar/entregar que ainda faltam:

- pacote solto: `manhattan(agente, pacote) + manhattan(pacote, meta) + 2`
- pacote na mão: `manhattan(agente, meta) + 1`

Ela ignora obstáculos e pedágios e conta cada ação como custo 1, que é o custo
mínimo possível. Então nunca superestima o custo real (**admissível**). Também é
**consistente**, porque cada ação muda o valor de `h` em no máximo o custo dela.

**A\* da `aigyminsper` e o `env()`:** a busca usa o `AEstrela` da biblioteca com
`pruning="general"`, que não adiciona à lista de abertos um nó cujo `env()` já foi
gerado. Testando contra uma busca de custo uniforme exata, encontramos:

- `pruning="without"` / `"father-son"`: plano ótimo, mas os mesmos estados são
  reabertos muitas vezes e a busca passa de 1 minuto já num grid 6×6;
- `pruning="general"` com `env()` = situação + custo da última ação: rápido, mas o
  plano deixou de ser ótimo em 5 de 300 mundos. A poda acontece quando o nó é
  **gerado**: se depois surge um caminho mais barato até o mesmo estado, ele é descartado.

Solução: o `env()` termina com o **custo acumulado** do caminho (`custo_acumulado`),
no lugar do custo da última ação. Assim a poda só descarta um nó que chega ao mesmo
estado **com o mesmo custo**, ou seja, um repetido de fato, e o plano ótimo é mantido.
Com isso, 500 mundos aleatórios deram custo ótimo, e um grid 40×40 resolve em menos
de meio segundo.

## Mundo sem solução

Antes do A\*, `existe_solucao()` faz uma busca em largura simples no grid:
existe plano se, e somente se, o agente alcança o pacote **e** o pacote alcança o
destino desviando dos obstáculos. Caso contrário, o programa informa que não existe
solução. Essa verificação é necessária: como o `env()` inclui o custo acumulado, num
mundo sem solução o `AEstrela` continuaria gerando caminhos cada vez mais caros e
não terminaria.

## Testes

`testes.py` verifica o mundo da prova (custo 9), um mundo sem solução e 500 mundos
aleatórios de 2×2 a 15×15. Em todos, o custo do A\* é igual ao de uma busca de custo
uniforme exata, e o plano executado leva ao estado objetivo.

## Exemplos de execução

Ver a pasta `exemplos/`. Mundo da prova (A agente, P pacote, X destino, # obstáculo,
$ pedágio, * caminho):

```
A $ P          A * P
. # .    ->    . # *
. X .          . X *

Plano: direita ; direita ; pegar ; baixo ; baixo ; esquerda ; entregar
Ações: 7 | Custo: 9
```

O segundo `direita` custa 3 porque é executado na célula de pedágio.
