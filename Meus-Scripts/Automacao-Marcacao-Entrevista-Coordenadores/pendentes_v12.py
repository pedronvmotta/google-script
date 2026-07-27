"""Cruza pool ativo Fase 3 (87) com Alocacoes (12) e lista os que NAO estao na planilha."""
import csv, io, re, sys, unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent
ALLOC = BASE / "Entrevistas com Coordena - Alocações - Horários (12).csv"

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())

APROVADOS = [
    "Ana Carolina Lessa Maia","Ana Carolina Rodrigues Correia da Silva","Ana Clara Bilitário Trianon",
    "André Ferreira Guedes Kang","Anna Julia dos Santos Vieira","Antonio Gaida Coutinho Marques",
    "Arthur Gonsales Cadengue","Arthur Yuan da Costa","Beatriz Martins Soares Ramires Savino",
    "Bernardo Borelli Mourelle","Bernardo Pereira Costa","Breno Almeida Monteiro",
    "Breno Ribeiro Palma de Souza","Bruno Fayad Cipolla","Caio Nogueira Silva Costa Guedes Pereira",
    "Caio Ongarato de Arruda","Camila Silva Novitsky","Camile dos Santos Silva",
    "Daniel Cesar Grancieri do Amaral","Eduardo Augusto Pinto Martins","Enrico Almeida Machado Dias de Souza",
    "Felipe Figueiras Nahid Pereira","Felipe Onoda Pessanha Bianchi","Flávio Magyar Ortolan Pereira",
    "Francisco Oliveira Navarro","Gabriel Michaeli dos Santos","Gabriel Torres dos Anjos",
    "Gabriela Lara Leuzinger","Gabriela Pereira de Souza","Gisele Ramos dos Santos Silva",
    "Giuliana Olivia Silva de Lima","Guilherme Weber Carvalho Pinto",
    "Helena Ayrão Venancio da Silva Franco Quintella Mendes","Henrique de Noronha Souto",
    "Hugo Nazare Boher e Souza Estrada Alves","Isabela Gluck Clemente","Isamu Nakandakara Ono",
    "João Marcelo da Gama Nóbrega Costa Pereira","João Pedro de Carvalho Urquiza",
    "João Pedro Pereira da Silva Santos","João Vitor Carreira Allak","Júlia Nascimento Pereira Rosa",
    "Júlio Kaléo Fernandes Oiticica Santos","Kayo Enzo Oliveira da Silva","Larissa Castro de Oliveira",
    "Leonardo de Sá Berbat","Leonardo Marques de Vasconcelos Gomes","Leonardo Rodrigues Vieira",
    "Leticia Freixo Amorim","Lucas Andrade Silva","Lucas Costa Sousa Gomes","Lucas de Oliveira Batista",
    "Luís Filipe Gois Alves das Neves","Luísa Leal Ávila","Luiz Henrique Guerrieri Rzetelny",
    "Marcelo Lôbo Nogueira Santos","Marcus Vinícius Alves Leandro","Maria Eduarda Giordano",
    "Maria Fernanda Castello Branco Pereira","Mariana Ferreira Rodrigues Peixoto",
    "Mariana Rocha de Oliveira Ferreira","Mateus Pereira Dutra","Matheus Brito Tosta da Silva",
    "Matheus da Silva Conceição","Matheus Duffles Pinheiro Vieira","Matheus Henriques Lara Resende",
    "Matheus Maroñas Varela","Matheus Viana Gomes","Miguel Antonio Guimarães de Abreu Lima",
    "Miguel Crespo Nogueira","Miguel Felipe Pinto Licurgo de Barros","Mirella da Silva Reis",
    "Nicoly Maia Santos","Olivia Jiale Xiao","Peterson Marques de Carvalho",
    "Rafael Wisnescky Gomes da Silva","Rayka Kamyly da Silva Constancio","Samara Bruna Wanderley Chagas",
    "Samuel Mendonça Ferreira","Sarah Siqueira de Paiva","Sofia Marques Novaes Valério",
    "Sophia Oliveira do Souto","Sophia Palmeira Melo","Sophia Souza Tiburcio","Stella Daniel Breitinger",
    "Tiago de Góis Paz","Tiago Medalha Mouro Pazos",
]

# Fora do pool ativo (reprovado Fase 3)
FORA = {norm("Kayo Enzo Oliveira da Silva")}
pool = [n for n in APROVADOS if norm(n) not in FORA]

# Nomes na Alocacoes (12) - coluna H (index 7)
na_planilha = set()
linhas_por_nome = {}
with open(ALLOC, encoding="utf-8") as f:
    for i, r in enumerate(list(csv.reader(f))[3:]):
        if len(r) > 7 and r[7].strip():
            n = norm(r[7])
            na_planilha.add(n)
            linhas_por_nome.setdefault(n, r[7].strip())

# Caso Caio Nogueira - CSV usa "guedes pereira", planilha usa "Chaffin guedes pereira"
# Vamos fazer match com "guedes pereira" tambem
alias = {
    norm("Caio Nogueira Silva Costa Guedes Pereira"): [
        "chaffin guedes pereira",
        "caio ongarato",  # cuidado NAO confundir
    ],
}

def esta_na_planilha(nome_pool):
    n = norm(nome_pool)
    if n in na_planilha:
        return True
    # match por sobrenome-chave para casos conhecidos
    if "caio nogueira" in n or "guedes pereira" in n:
        for x in na_planilha:
            if "guedes pereira" in x and "ongarato" not in x:
                return True
    return False

fora_planilha = [n for n in pool if not esta_na_planilha(n)]

print(f"Pool ativo Fase 3: {len(pool)}")
print(f"Nomes distintos na Alocacoes (12): {len(na_planilha)}")
print(f"Pool que NAO esta na planilha: {len(fora_planilha)}")
print()
print("=" * 70)
print("NAO estao na Alocacoes (12) — precisam ser marcados:")
print("=" * 70)
for n in fora_planilha:
    print(f"  - {n}")
