#Interface gráfica (tkinter, já vem com o Python).
# O usuário escolhe a dimensão, gera um mundo aleatório, resolve com A* e assiste o agente executando o plano.

import tkinter as tk
from tkinter import ttk
from busca import resolver
from mundo import gerar_mundo

TAMANHO_CANVAS = 560

CORES = {
    "fundo": "#ffffff",
    "linha": "#2b2b2b",
    "obstaculo": "#141414",
    "pedagio": "#b9bcc2",
    "caminho": "#cfe3ff",
    "agente": "#1f6f8b",
    "pacote": "#e8a33d",
    "pacote_borda": "#8a5a12",
    "meta": "#d62828",
}


class Aplicacao:

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Entregador no Grid — A*")
        self.mundo = None
        self.resultado = None
        self.animacao = None   # id do raiz.after() da animação em andamento

        # painel de controles
        painel = ttk.Frame(raiz, padding=12)
        painel.grid(row=0, column=0, sticky="ns")

        ttk.Label(painel, text="Dimensão do grid (n × n)").grid(row=0, column=0, sticky="w")
        self.dimensao = tk.IntVar(value=10)
        ttk.Spinbox(painel, from_=2, to=40, textvariable=self.dimensao, width=8).grid(
            row=1, column=0, sticky="w", pady=(2, 10))

        ttk.Button(painel, text="Gerar mundo aleatório", command=self.gerar).grid(
            row=2, column=0, sticky="ew", pady=2)
        self.botao_resolver = ttk.Button(painel, text="Resolver (A*)", command=self.resolver,
                                         state="disabled")
        self.botao_resolver.grid(row=3, column=0, sticky="ew", pady=2)
        self.botao_animar = ttk.Button(painel, text="Animar plano", command=self.animar,
                                       state="disabled")
        self.botao_animar.grid(row=4, column=0, sticky="ew", pady=2)

        self.status = tk.StringVar(value="Escolha a dimensão e gere um mundo.")
        ttk.Label(painel, textvariable=self.status, wraplength=220, justify="left").grid(
            row=5, column=0, sticky="w", pady=(12, 6))

        ttk.Label(painel, text="Plano:").grid(row=6, column=0, sticky="w")
        self.lista_plano = tk.Listbox(painel, height=18, width=28)
        self.lista_plano.grid(row=7, column=0, sticky="nsew")

        legenda = ("Legenda: ● agente   ■ pacote   ✕ destino\n"
                   "preto = obstáculo   cinza = pedágio (+2)\n"
                   "azul claro = caminho do plano")
        ttk.Label(painel, text=legenda, justify="left", foreground="#555").grid(
            row=8, column=0, sticky="w", pady=(10, 0))

        # desenho do grid
        self.canvas = tk.Canvas(raiz, width=TAMANHO_CANVAS, height=TAMANHO_CANVAS,
                                bg=CORES["fundo"], highlightthickness=0)
        self.canvas.grid(row=0, column=1, padx=12, pady=12)

    # ações dos botões
    def gerar(self):
        self.parar_animacao()
        try:
            n = int(self.dimensao.get())
        except (tk.TclError, ValueError):
            self.status.set("Dimensão inválida.")
            return
        if n < 2:
            self.status.set("A dimensão mínima é 2.")
            return

        self.mundo = gerar_mundo(n)
        self.resultado = None
        self.lista_plano.delete(0, tk.END)
        self.botao_resolver.config(state="normal")
        self.botao_animar.config(state="disabled")
        self.status.set(f"Mundo {n}×{n} gerado: {len(self.mundo['obstaculos'])} obstáculos, "
                        f"{len(self.mundo['pedagios'])} pedágios.")
        self.desenhar(self.mundo["agente"], self.mundo["pacote"], False)

    def resolver(self):
        if self.mundo is None:
            return
        self.parar_animacao()
        self.resultado = resolver(self.mundo)
        self.lista_plano.delete(0, tk.END)

        if not self.resultado["solucao"]:
            self.status.set("NÃO EXISTE SOLUÇÃO: o agente não consegue alcançar o pacote "
                            "ou levar o pacote até o destino.")
            self.botao_animar.config(state="disabled")
            self.desenhar(self.mundo["agente"], self.mundo["pacote"], False)
            return

        for i, acao in enumerate(self.resultado["plano"], start=1):
            self.lista_plano.insert(tk.END, f"{i:>3}. {acao}")
        self.status.set(f"Plano ótimo encontrado.\n"
                        f"Ações: {len(self.resultado['plano'])}   "
                        f"Custo: {self.resultado['custo']}")
        self.botao_animar.config(state="normal")
        self.desenhar(self.mundo["agente"], self.mundo["pacote"], False, mostrar_caminho=True)

    def animar(self, passo=0):
        if not self.resultado or not self.resultado["solucao"]:
            return
        if passo == 0:
            self.parar_animacao()
        estados = self.resultado["estados"]
        estado = estados[passo]
        self.desenhar(estado.pos_agente, estado.pos_pacote, estado.com_agente,
                      mostrar_caminho=True)
        if passo > 0:
            self.lista_plano.selection_clear(0, tk.END)
            self.lista_plano.selection_set(passo - 1)
            self.lista_plano.see(passo - 1)
        if passo + 1 < len(estados):
            self.animacao = self.raiz.after(350, self.animar, passo + 1)
        else:
            self.animacao = None

    def parar_animacao(self):
        if self.animacao is not None:
            self.raiz.after_cancel(self.animacao)
            self.animacao = None

    # desenho
    def desenhar(self, pos_agente, pos_pacote, com_agente, mostrar_caminho=False):
        m = self.mundo
        n = m["dimensao"]
        lado = TAMANHO_CANVAS / n
        self.canvas.delete("all")

        caminho = set()
        if mostrar_caminho and self.resultado and self.resultado["solucao"]:
            caminho = {e.pos_agente for e in self.resultado["estados"]}

        def retangulo(l, c):
            return c * lado, l * lado, (c + 1) * lado, (l + 1) * lado

        # células
        for l in range(n):
            for c in range(n):
                pos = (l, c)
                if pos in m["obstaculos"]:
                    cor = CORES["obstaculo"]
                elif pos in m["pedagios"]:
                    cor = CORES["pedagio"]
                elif pos in caminho:
                    cor = CORES["caminho"]
                else:
                    cor = CORES["fundo"]
                self.canvas.create_rectangle(*retangulo(l, c), fill=cor, outline=CORES["linha"])
                # pedágio que também está no caminho: borda azul
                if pos in m["pedagios"] and pos in caminho:
                    x0, y0, x1, y1 = retangulo(l, c)
                    self.canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                                                 outline=CORES["agente"], width=2)

        margem = lado * 0.2

        # destino (X)
        x0, y0, x1, y1 = retangulo(*m["meta"])
        largura = max(2, int(lado * 0.08))
        self.canvas.create_line(x0 + margem, y0 + margem, x1 - margem, y1 - margem,
                                fill=CORES["meta"], width=largura)
        self.canvas.create_line(x0 + margem, y1 - margem, x1 - margem, y0 + margem,
                                fill=CORES["meta"], width=largura)

        # pacote (quando não está com o agente)
        if not com_agente:
            x0, y0, x1, y1 = retangulo(*pos_pacote)
            self.canvas.create_rectangle(x0 + margem, y0 + margem, x1 - margem, y1 - margem,
                                         fill=CORES["pacote"], outline=CORES["pacote_borda"],
                                         width=2)

        # agente
        x0, y0, x1, y1 = retangulo(*pos_agente)
        self.canvas.create_oval(x0 + margem, y0 + margem, x1 - margem, y1 - margem,
                                fill=CORES["agente"], outline="")
        if com_agente:
            # pacote "na mão": quadradinho no canto da célula do agente
            s = lado * 0.3
            self.canvas.create_rectangle(x1 - s, y1 - s, x1 - 2, y1 - 2,
                                         fill=CORES["pacote"], outline=CORES["pacote_borda"])

def executar():
    raiz = tk.Tk()
    raiz.resizable(False, False)
    Aplicacao(raiz)
    raiz.mainloop()
