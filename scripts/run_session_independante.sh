#!/bin/sh
# Enveloppe de run_physical_tail.sh pour une session INDEPENDANTE (apres redemarrage complet).
# Ne modifie ni le code, ni run_physical_tail.sh, ni les parametres de mesure.
# Garanties ajoutees : (1) jamais d'ecrasement : etiquette unique obligatoire, refus si le dossier existe ;
# (2) identifiant de demarrage (boot_id) enregistre et refuse s'il a deja servi a une session ;
# (3) archive finale horodatee non ecrasable + SHA-256 ; (4) copie des CSV bruts dans l'archive.
# Usage (depuis ~/MAYO-C-A2) : sh run_session_independante.sh        # parametres par defaut : coeur 1, 3001 paires, graines 21..25
set -e
ROOT=$(pwd)
[ -f test/run_physical_tail.sh ] || { echo "Lancer depuis ~/MAYO-C-A2"; exit 1; }
BOOT=$(cat /proc/sys/kernel/random/boot_id)
LOG="$HOME/.a2_sessions.log"
touch "$LOG"
if grep -q "$BOOT" "$LOG" && [ -z "$FORCE_SAME_BOOT" ]; then
  echo "REFUS : ce demarrage (boot_id $BOOT) a deja servi a une session. Redemarrer completement la machine."; exit 1
fi
UPS=$(cut -d. -f1 /proc/uptime)
[ "$UPS" -le 5400 ] || echo "ATTENTION : uptime $((UPS/60)) min (> 90 min). Une session independante suppose une mesure peu apres le redemarrage."
SESSION=${SESSION:-s5_$(date +%Y%m%d_%H%M%S)}
OUT="$ROOT/physical_tail_$(hostname)_$SESSION"
[ ! -e "$OUT" ] || { echo "REFUS : $OUT existe deja (pas d'ecrasement). Changer SESSION."; exit 1; }
echo "$BOOT $SESSION $(date -u +%FT%TZ)" >> "$LOG"
export SESSION OUT
sh test/run_physical_tail.sh 1 3001 "${SEEDS:-21 22 23 24 25}"
{ echo "== boot_id"; echo "$BOOT"; echo "== uptime au lancement (s)"; echo "$UPS"; echo "== uptime -s"; uptime -s; } >> "$OUT/machine.txt"
ARCH="$ROOT/${SESSION}_$(hostname)_$(date +%Y%m%d_%H%M%S).tar.gz"
[ ! -e "$ARCH" ] || { echo "REFUS : $ARCH existe"; exit 1; }
tar czf "$ARCH" --exclude='build_*' -C "$ROOT" "$(basename "$OUT")"
sha256sum "$ARCH" | tee "$ARCH.sha256"
echo "Archive complete (CSV bruts inclus) : $ARCH"
