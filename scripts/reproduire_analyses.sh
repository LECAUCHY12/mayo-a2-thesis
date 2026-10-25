#!/bin/sh
# Reproduit TOUTES les analyses chiffrees de la synthese a partir des trois archives A2_partie{1,2,3}.tar.gz
# et verifie que chaque sortie est identique a celle livree (espaces de fin de ligne ignores ; les lignes "--- S1 (chemin)" qui rappellent le chemin local sont ignorees).
# Usage : sh reproduire_analyses.sh <dossier_contenant_A2_partie1.tar.gz_A2_partie2.tar.gz_A2_partie3.tar.gz> <dossier_de_travail_NEUF>
# Prerequis : python3 + numpy, tar, sha256sum. Duree : < 1 minute.
set -e
SRC=$(cd "$1" && pwd); W=$2
[ -n "$W" ] && [ ! -e "$W" ] || { echo "Donner un dossier de travail qui n'existe pas"; exit 1; }
mkdir -p "$W" && cd "$W"
for i in 1 2 3; do tar xzf "$SRC/A2_partie$i.tar.gz"; ( cd A2_partie$i && sha256sum -c SHA256SUMS.txt >/dev/null ) && echo "partie$i : empreintes internes OK"; done
mkdir s1root s2root ph ct
tar xzf A2_partie3/A2_donnees_brutes_session1_4campagnes.tar.gz -C s1root
tar xzf A2_partie1/s5_20261020_141008_cauchy_20261020_143254.tar.gz -C s2root
tar xzf A2_partie2/phases_cauchy_ph1_20261021_211304.tar.gz -C ph
tar xzf A2_partie2/controle_cauchy_ct1_20261021_212841.tar.gz -C ct
S=A2_partie1/scripts; A=A2_partie1/analyses; PH=ph/phases_cauchy_ph1_20261021_211304
chk() { a=$(sed -e "s/ *$//" -e "/^--- S[12] (/d" "$1" | sha256sum); b=$(sed -e "s/ *$//" -e "/^--- S[12] (/d" "$2" | sha256sum); if [ "$a" = "$b" ]; then echo "OK    $2"; else echo "ECART $2"; fi; }
run() { out=$1; ref=$2; shift 2; python3 -I "$@" > "$out" 2>&1; chk "$out" "$A/$ref"; }
run o1.txt synthese_safe.txt                      $S/synthese_sessions.py s1root s2root safe
run o2.txt synthese_default.txt                   $S/synthese_sessions.py s1root s2root default
run o3.txt analyse_comparaison_S1_S2_safe.txt     $S/compare_sessions.py s1root s2root safe
run o4.txt analyse_comparaison_S1_S2_default.txt  $S/compare_sessions.py s1root s2root default
run o5.txt phases_MAYO5_decomposition.txt         $S/phases_analyze.py "$PH/csv_phases/phases_m5_s*.csv"
run o6.txt phases_MAYO1_decomposition.txt         $S/phases_analyze.py "$PH/csv_phases/phases_m1_s*.csv"
run o7.txt phases_MAYO2_temoin_nul.txt            $S/phases_analyze.py "$PH/csv_phases/phases_m2_s*.csv"
run o8.txt phases_avec_vs_sans_sondes.txt         $S/phases_vs_ref.py "$PH"
run o9.txt controle_sondes_resultats.txt          $S/controle_analyze.py ct/controle_cauchy_ct1_20261021_212841
