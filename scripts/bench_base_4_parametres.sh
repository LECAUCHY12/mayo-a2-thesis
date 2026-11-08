#!/bin/sh
# Temps de base du code OFFICIEL (AVX2) pour MAYO-1, 2, 3 et 5 : keypair, expand_sk, expand_pk, sign, verify, open.
# Utilise le programme de mesure fourni par MAYO-C (mayo_bench_MAYO_N <essais>), sans aucune de nos modifications A2.
# Usage (depuis le dossier MAYO-C-mesures) : sh ~/…/bench_base_4_parametres.sh [coeur=1] [essais=1000] [repetitions=5]
# Sortie : dossier bench_base_<machine>_<date>/ avec machine.txt, sortie_<param>_<n>.txt, resume.txt. Les valeurs sont en ticks TSC (rdtsc).
set -e
ROOT=$(pwd); [ -f "$ROOT/CMakeLists.txt" ] && [ -d "$ROOT/src" ] || { echo "REFUS : lancer depuis le dossier MAYO-C"; exit 1; }
CORE=${1:-1}; RUNS=${2:-1000}; REP=${3:-5}
OUT=${OUT:-$ROOT/bench_base_$(hostname)_$(date +%Y%m%d_%H%M%S)}
[ ! -e "$OUT" ] || { echo "REFUS : $OUT existe deja"; exit 1; }
mkdir -p "$OUT/build" && cd "$OUT/build"
{ date -u; uname -a; gcc --version | head -1; cmake --version | head -1; lscpu | head -20
  echo "governor: $(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_governor 2>/dev/null || echo n/a)"
  echo "no_turbo: $(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || echo n/a)"
  echo "arbre: $(cd "$ROOT" && git rev-parse 'HEAD^{tree}' 2>/dev/null || echo n/a)"
  echo "arguments: coeur=$CORE essais=$RUNS repetitions=$REP"; } > "$OUT/machine.txt" 2>&1
cmake "$ROOT" -DMAYO_BUILD_TYPE=avx2 "-DMAYO_MARCH=-march=haswell -maes" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON > cmake.log 2>&1
make -j"$(nproc)" mayo_bench_MAYO_1 mayo_bench_MAYO_2 mayo_bench_MAYO_3 mayo_bench_MAYO_5 > make.log 2>&1
cd test
for r in $(seq 1 "$REP"); do
  for v in 1 2 3 5; do
    taskset -c "$CORE" "./mayo_bench_MAYO_$v" "$RUNS" > "$OUT/sortie_MAYO${v}_$r.txt" 2>&1
  done
done
{ echo "Mediane des ticks par operation, pour chaque repetition (code officiel AVX2, $RUNS essais)"; for v in 1 2 3 5; do echo "== MAYO-$v"; cat "$OUT"/sortie_MAYO${v}_*.txt | grep -E "median" ; done; } | tee "$OUT/resume.txt"
