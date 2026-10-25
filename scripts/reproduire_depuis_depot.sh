#!/bin/sh
# Reproduit les 9 analyses chiffrees a partir des DONNEES BRUTES du depot (data/raw/) et les compare a analyses/.
# Usage (depuis la racine du depot) : sh scripts/reproduire_depuis_depot.sh <dossier_de_travail_NEUF>
# Prerequis : python3 + numpy, tar, sha256sum. Duree : < 1 minute. Ne modifie rien dans le depot.
set -e
R=$(pwd); W=$1
[ -n "$W" ] && [ ! -e "$W" ] || { echo "Donner un dossier de travail qui n'existe pas"; exit 1; }
( cd data/raw && sha256sum -c SHA256SUMS.txt ) || { echo "Archives brutes alterees"; exit 1; }
mkdir -p "$W" && cd "$W"
mkdir s1root s2root ph ct
tar xzf "$R/data/raw/A2_donnees_brutes_session1_4campagnes.tar.gz" -C s1root
tar xzf "$R/data/raw/s5_20261020_141008_cauchy_20261020_143254.tar.gz" -C s2root
tar xzf "$R/data/raw/phases_cauchy_ph1_20261021_211304.tar.gz" -C ph
tar xzf "$R/data/raw/controle_cauchy_ct1_20261021_212841.tar.gz" -C ct
S=$R/scripts; A=$R/analyses; PH=ph/phases_cauchy_ph1_20261021_211304
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
