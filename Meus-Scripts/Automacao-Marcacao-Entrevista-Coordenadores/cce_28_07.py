"""CCE disponivel em 28/07 x Gabriel Santos — filtra pool ativo, ja marcados, indisponibilidades pontuais."""
import csv, io, re, sys, unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent
ALLOC = BASE / "Entrevistas com Coordena - Alocações - Horários (11).csv"
CAND  = BASE / "E.C Candidatos - disponibilidade  (respostas) - Respostas ao formulário 1 (4).csv"
COORD = BASE / "Coordenas - disponibilidade (respostas) - Respostas ao formulário 1 (1).csv"

DIAS = ["14/07","15/07","16/07","17/07","20/07","21/07","22/07","23/07","24/07","27/07","28/07","29/07"]
DIA = "28/07"
IDX = DIAS.index(DIA)
HORARIOS = ["10h","11h","13h","14h","15h","16h","17h"]
NO_AVAIL = "Não tenho disponibilidade nenhum horário"

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())

def parse_h(cell):
    if not cell or NO_AVAIL in cell: return set()
    return {h.strip() for h in re.findall(r"\d+h", cell)}

# --- Alocacao: quem ja apareceu (marcado futuro OU ja fez)
ja_marcados = set()
with open(ALLOC, encoding="utf-8") as f:
    for r in list(csv.reader(f))[3:]:
        if len(r) > 7 and r[7].strip():
            ja_marcados.add(norm(r[7]))

# --- Ignorar (reprovados/desistentes/pontuais 28/07)
IGNORAR = {norm(n) for n in [
    "Michel Leandro Machado", "Tainá Ribeiro dos Santos",
    "Adriana Rodrigues dos Santos da Cruz", "Kayo Enzo",
]}
INDISP_28 = {norm("Sophia Souza Tiburcio")}  # avisou 27/07 que nao vai em 28/07

# --- Candidatos CCE (pega o registro mais recente por email/nome)
cand = {}
with open(CAND, encoding="utf-8") as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row) < 5 or not row[1].strip(): continue
        area = row[3].strip()
        if area != "CCE": continue
        nome = row[1].strip()
        email = row[2].strip().lower()
        key = email or norm(nome)
        disp = {}
        for i, d in enumerate(DIAS):
            col = 4 + i
            disp[d] = parse_h(row[col]) if col < len(row) else set()
        cand[key] = {"nome": nome, "disp": disp}

# --- Coordena Gabriel Santos
gabriel = None
with open(COORD, encoding="utf-8") as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if row[3].strip() == "CCE":
            disp = parse_h(row[4 + IDX])
            gabriel = {"nome": row[1].strip(), "disp_28": disp}

print(f"Gabriel Santos disp 28/07: {sorted(gabriel['disp_28'], key=lambda x: HORARIOS.index(x))}")
print()

# --- Cruzar
disponiveis = []
sem_disp = []
ja_marcados_cce = []
ignorados = []

for k, c in cand.items():
    n = norm(c["nome"])
    if n in ja_marcados:
        ja_marcados_cce.append(c["nome"])
        continue
    if n in IGNORAR:
        ignorados.append(c["nome"] + " (reprovado/desistente)")
        continue
    if n in INDISP_28:
        ignorados.append(c["nome"] + " (avisou que nao vai em 28/07)")
        continue
    slots_cand = c["disp"].get(DIA, set())
    overlap = slots_cand & gabriel["disp_28"]
    if overlap:
        disponiveis.append((c["nome"], overlap))
    elif slots_cand:
        sem_disp.append((c["nome"], slots_cand, "sem overlap c/ Gabriel"))
    else:
        sem_disp.append((c["nome"], set(), "sem disp em 28/07"))

print("=" * 80)
print(f"CCE PENDENTES com overlap Gabriel Santos em 28/07 ({len(disponiveis)}):")
print("=" * 80)
for nome, ov in sorted(disponiveis):
    slots = sorted(ov, key=lambda x: HORARIOS.index(x))
    print(f"  {nome:<45} slots: {', '.join(slots)}")

print()
print("=" * 80)
print(f"CCE PENDENTES sem match em 28/07 ({len(sem_disp)}):")
print("=" * 80)
for nome, slots, motivo in sorted(sem_disp):
    s = ', '.join(sorted(slots, key=lambda x: HORARIOS.index(x) if x in HORARIOS else 99)) if slots else "-"
    print(f"  {nome:<45} disp: {s:<30} ({motivo})")

print()
print(f"Info: {len(ja_marcados_cce)} CCE ja marcados/entrevistados; {len(ignorados)} ignorados")
if ignorados:
    for i in ignorados:
        print(f"  - {i}")
