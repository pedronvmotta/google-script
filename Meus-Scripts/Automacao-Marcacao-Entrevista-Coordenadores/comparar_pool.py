"""Compara o pool oficial informado pelo usuario com o CSV E.C Candidatos."""
import csv
import io
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent
CAND = BASE / "E.C Candidatos - disponibilidade  (respostas) - Respostas ao formulário 1 (2).csv"

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())

# Pool oficial do usuario (89 nomes)
oficial_raw = """Ana Carolina Lessa Maia
Ana Carolina Rodrigues Correia da Silva
Ana Clara Bilitário Trianon
André Ferreira Guedes Kang
Anna Julia dos Santos Vieira
Antonio Gaida Coutinho Marques
Arthur Gonsales Cadengue
Arthur Yuan da Costa
beatriz martins soares ramires savino
Bernardo Borelli Mourelle
Bernardo Pereira Costa
Breno Almeida Monteiro
Breno Ribeiro Palma de Souza
Bruno Fayad Cipolla
Caio Nogueira silva costa guedes pereira
Caio Ongarato de Arruda
Camila Silva Novitsky
Camile dos Santos Silva
Daniel Cesar Grancieri do Amaral
EDUARDO AUGUSTO PINTO MARTINS
ENRICO ALMEIDA MACHADO DIAS DE SOUZA
Felipe Figueiras Nahid Pereira
Felipe Onoda Pessanha Bianchi
Flávio Magyar Ortolan Pereira
Francisco Oliveira Navarro
Gabriel Michaeli dos Santos
Gabriel Torres dos anjos
Gabriela Lara Leuzinger
Gabriela Pereira de Souza
Gisele Ramos dos Santos Silva
Giuliana Olivia Silva de Lima
Guilherme Weber Carvalho Pinto
Helena Ayrão Venancio da Silva Franco Quintella Mendes
Henrique de Noronha Souto
Hugo Nazare Boher e Souza Estrada Alves
Isabela Gluck Clemente
Isamu Nakandakara Ono
João Marcelo da Gama Nóbrega Costa Pereira
João Pedro de Carvalho Urquiza
João Pedro Pereira da Silva Santos
João Vitor Carreira Allak
Júlia Nascimento Pereira Rosa
Júlio Kaléo Fernandes Oiticica Santos
Kayo Enzo Oliveira da Silva
Larissa Castro de Oliveira
Leonardo de Sá Berbat
Leonardo Marques de Vasconcelos Gomes
Leonardo Rodrigues Vieira
Letícia Freixo Amorim
Lucas Andrade Silva
Lucas Costa Sousa Gomes
Lucas de Oliveira Batista
Luís Filipe Gois Alves das Neves
Luísa Leal Ávila
LUIZ HENRIQUE GUERRIERI RZETELNY
Marcelo Lôbo Nogueira Santos
Marcus Vinícius Alves Leandro
Maria Eduarda Giordano
Maria Fernanda Castello Branco Pereira
Maria Gabriela Araujo de Oliveira
Mariana Ferreira Rodrigues Peixoto
Mariana Rocha de Oliveira Ferreira
Mateus Pereira Dutra
Matheus Brito Tosta da Silva
Matheus da Silva Conceição
Matheus Duffles Pinheiro Vieira
Matheus Henriques Lara Resende
Matheus Maroñas Varela
Matheus Viana Gomes
Miguel Antonio Guimarães de Abreu Lima
Miguel Crespo Nogueira
Miguel Felipe Pinto Licurgo de Barros
Mirella da Silva Reis
Nicoly Maia Santos
Olivia Jiale Xiao
Peterson Marques de Carvalho
Rafael Wisnescky Gomes da Silva
Rayka kamyly da Silva Constancio
Rodrigo Jales Carneiro da Silva
Samara Bruna Wanderley Chagas
Samuel Mendonça Ferreira
Sarah Siqueira de Paiva
Sofia Marques Novaes Valério
Sophia Oliveira do Souto
Sophia Palmeira Melo
Sophia Souza Tiburcio
Stella Daniel Breitinger
Tiago de Góis Paz
Tiago Medalha Mouro Pazos"""

oficial_list = [n.strip() for n in oficial_raw.splitlines() if n.strip()]
oficial_map = {norm(n): n.strip() for n in oficial_list}
print(f"Pool oficial (usuario): {len(oficial_list)} nomes")

# CSV
csv_list = []
with open(CAND, encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 4 or not row[1].strip(): continue
        csv_list.append(row[1].strip())
csv_map = {norm(n): n.strip() for n in csv_list}
print(f"CSV E.C Candidatos: {len(csv_list)} respostas ({len(csv_map)} nomes unicos)")

# Diferencas
so_oficial = set(oficial_map.keys()) - set(csv_map.keys())
so_csv = set(csv_map.keys()) - set(oficial_map.keys())

print()
print(f"=== NO POOL OFICIAL mas NAO no CSV ({len(so_oficial)}): ===")
for k in sorted(so_oficial):
    print(f"  • {oficial_map[k]}")

print()
print(f"=== NO CSV mas NAO no POOL OFICIAL ({len(so_csv)}): ===")
for k in sorted(so_csv):
    print(f"  • {csv_map[k]}")

print()
print(f"=== INTERSECAO ({len(set(oficial_map.keys()) & set(csv_map.keys()))}): OK ===")
