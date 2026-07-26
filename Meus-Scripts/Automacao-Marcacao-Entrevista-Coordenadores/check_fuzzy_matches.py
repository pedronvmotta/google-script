"""Detecta nomes que diferem entre CSV disponibilidade e planilha Alocação (subset match)."""
import csv
import io
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent
ALLOC = BASE / "Entrevistas com Coordena - Alocações - Horários (10).csv"
CAND = BASE / "E.C Candidatos - disponibilidade  (respostas) - Respostas ao formulário 1 (2).csv"

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())

def tokens(s):
    return set(norm(s).split())

# Nomes do CSV (candidatos)
csv_nomes = set()
with open(CAND, encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 4 or not row[1].strip(): continue
        csv_nomes.add(row[1].strip())

# Nomes da alocação
aloc_nomes = set()
with open(ALLOC, encoding="utf-8") as f:
    for r in csv.reader(f):
        if len(r) > 7 and r[7].strip():
            aloc_nomes.add(r[7].strip())

csv_norm = {norm(n): n for n in csv_nomes}
aloc_norm = {norm(n): n for n in aloc_nomes}

# Match exato
match_exato = set(csv_norm) & set(aloc_norm)
csv_nao_batidos = set(csv_norm) - match_exato
aloc_nao_batidos = set(aloc_norm) - match_exato

# Match por subset de tokens (>= 3 tokens iguais e um contido no outro OU >=80% overlap)
matches_fuzzy = []
for c in list(csv_nao_batidos):
    tc = tokens(c)
    if len(tc) < 2: continue
    for a in list(aloc_nao_batidos):
        ta = tokens(a)
        inter = tc & ta
        # Regra: pelo menos 3 tokens iguais e um é subset do outro (nome do meio adicional)
        if len(inter) >= 3 and (tc.issubset(ta) or ta.issubset(tc)):
            matches_fuzzy.append((c, a))

print(f"CSV: {len(csv_nomes)} nomes | Alocação: {len(aloc_nomes)} nomes marcados")
print(f"Match exato: {len(match_exato)}")
print(f"CSV nao batidos: {len(csv_nao_batidos)}")
print(f"Alocação nao batidos: {len(aloc_nao_batidos)}")
print()
print(f"=== MATCHES POR SUBSET DE TOKENS (candidato provavelmente marcado mas nao detectado) ===")
for c, a in matches_fuzzy:
    print(f"  CSV: {csv_norm[c]!r}")
    print(f"  ALO: {aloc_norm[a]!r}")
    print()

print("=== Alocação SEM MATCH nenhum no CSV (nomes marcados que nao existem no CSV) ===")
casados = {a for _, a in matches_fuzzy}
for a in sorted(aloc_nao_batidos):
    if a in casados: continue
    print(f"  • {aloc_norm[a]}")
