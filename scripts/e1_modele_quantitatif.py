#!/usr/bin/env python3
"""Modele quantitatif elementaire (MAYO-5, GCC 16.2.0) : relie les comptes STATIQUES d'instructions par entree (E1)
aux temps MESURES (PH1 et CT1, ticks TSC). Aucune mesure nouvelle. Les entrees ci-dessous sont recopiees des sorties
livrees ; leur provenance est indiquee. Le modele n'etablit pas de causalite : il teste la coherence des ordres de grandeur.
Usage : python3 -I e1_modele_quantitatif.py"""
NENT = 142 * 143 // 2            # entrees de P1 (MAYO-5, v = 142) = 10153

# --- Comptes statiques par entree (data/e1_gcc16/e1_gcc16_analyse.txt ; e1_inline_attrib.py) ---
# P1 officiel en contexte : boucle identifiee par POSITION et DECOMPTE (123 instr., 36 vpshufb), pas par marqueur (code fusionne).
instr = {  # (config) : (P1 off, P1 A2, P1t off, P1t A2)
    "banc isole":               (124, 106, 126, 110),
    "contexte, toutes sondes":  (123, 105, 126, 109),
    "contexte, sans sondes":    (123, 135, 162, 139),
}
# --- Temps mesures, ticks TSC par signature (analyses/phases_MAYO5_decomposition.txt ; controle_sondes_resultats.txt) ---
ph1 = dict(p1_off=268513, p1_a2=214345, p1t_off=367168, p1t_a2=321152, mc_off=805136, mc_a2=705398)
ct1_mcalc = dict(total_off=1502948, total_a2=1483529, reste_off=566917, reste_a2=567323)   # config 'mcalc'
mc_none_off = ct1_mcalc["total_off"] - ct1_mcalc["reste_off"]   # m_calculate, contexte sans autres sondes
mc_none_a2 = ct1_mcalc["total_a2"] - ct1_mcalc["reste_a2"]

print("1) rapports A2/officiel : instructions statiques (P1+P1t) contre temps mesures")
for k, (a, b, c, d) in instr.items():
    print("   %-26s instr A2/off = %.3f (gain statique %.1f %%)" % (k, (b + d) / (a + c), 100 * (1 - (b + d) / (a + c))))
p = ph1
print("   mesure toutes sondes : P1+P1t  %d -> %d  (gain %.1f %%) ; m_calculate %d -> %d (gain %.1f %%)" % (
    p["p1_off"] + p["p1t_off"], p["p1_a2"] + p["p1t_a2"], 100 * (1 - (p["p1_a2"] + p["p1t_a2"]) / (p["p1_off"] + p["p1t_off"])),
    p["mc_off"], p["mc_a2"], 100 * (1 - p["mc_a2"] / p["mc_off"])))
print("   mesure sans sondes (config mcalc) : m_calculate %d -> %d  (gain %.1f %%)" % (mc_none_off, mc_none_a2, 100 * (1 - mc_none_a2 / mc_none_off)))

c0 = (p["p1_off"] + p["p1t_off"]) / ((instr["contexte, toutes sondes"][0] + instr["contexte, toutes sondes"][2]) * NENT)
print("\n2) etalonnage sur 'toutes sondes' : %.3f tick par instruction statique" % c0)
a, b, c, d = instr["contexte, sans sondes"]
pred_off, pred_a2 = c0 * (a + c) * NENT, c0 * (b + d) * NENT
print("   prediction sans sondes : P1+P1t officiel %.0f, A2 %.0f, gain %.0f ticks (mesure : gain m_calculate %d ticks)" % (
    pred_off, pred_a2, pred_off - pred_a2, mc_none_off - mc_none_a2))

print("\n3) cout des ecritures supplementaires (sans sondes moins toutes sondes), par bras")
extra_off = (instr["contexte, sans sondes"][2] - instr["contexte, toutes sondes"][2]) * NENT          # P1t officiel : +36 ; P1 officiel : 0
extra_a2 = ((instr["contexte, sans sondes"][1] - instr["contexte, toutes sondes"][1]) +
            (instr["contexte, sans sondes"][3] - instr["contexte, toutes sondes"][3])) * NENT          # P1 A2 +30, P1t A2 +30
dt_off, dt_a2 = mc_none_off - p["mc_off"], mc_none_a2 - p["mc_a2"]
print("   officiel : %d instr. en plus (P1+P1t) ; m_calculate +%d ticks -> %.3f tick/instr. en plus" % (extra_off, dt_off, dt_off / extra_off))
print("   A2       : %d instr. en plus (P1+P1t) ; m_calculate +%d ticks -> %.3f tick/instr. en plus" % (extra_a2, dt_a2, dt_a2 / extra_a2))
print("   (Ut_times_O et m_lambda_times_O ont aussi +37 instr. dans les deux bras ; leur nombre de tours n'est pas connu ici.)")
