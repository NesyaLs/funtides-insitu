#!/usr/bin/env bash
set -euo pipefail

BIN="$(pwd)/build/bin/semproxy"
DT=0.001
TIMEMAX=1.5
EX=100
EY=100
EZ=1
INTERVAL=50

OUTDIR="$(pwd)/test_100_$(date +%Y%m%d_%H%M%S)"
INSITU_DIR="$OUTDIR/insitu"
ADHOC_DIR="$OUTDIR/adhoc"
mkdir -p "$INSITU_DIR" "$ADHOC_DIR"

read_last_metrics() {
  local metrics_json="$1"
  python3 - "$metrics_json" <<'PY'
import json, sys
p=sys.argv[1]
with open(p,"r") as f:
    arr=json.load(f)
m=arr[-1]
print(m.get("compute_time",0), m.get("output_time",0), m.get("snapshot_size_bytes",0))
PY
}

# -------- INSITU (light) --------
INSITU_CSV="$INSITU_DIR/pressure_insitu.csv"
INSITU_CMD="./semproxy --ex $EX --ey $EY --ez $EZ --dt $DT --timemax $TIMEMAX \
  --pressure-insitu --pressure-insitu-mode light \
  --pressure-stats-interval $INTERVAL --pressure-stats-file pressure_insitu.csv"

cp "$BIN" "$INSITU_DIR/semproxy"
echo "$INSITU_CMD" > "$INSITU_DIR/command.txt"
( cd "$INSITU_DIR" && bash -lc "$INSITU_CMD" >/dev/null )

INSITU_METRICS="$INSITU_DIR/snapshot_metrics/metrics.json"
read -r INSITU_COMP INSITU_OUT INSITU_BYTES < <(read_last_metrics "$INSITU_METRICS")
INSITU_TOTAL_SIM=$(python3 - <<PY
c=float("$INSITU_COMP"); o=float("$INSITU_OUT")
print(f"{c+o:.6f}")
PY
)

# -------- ADHOC (snapshots + post) --------
SNAPDIR="$ADHOC_DIR/snapshots"
mkdir -p "$SNAPDIR"
ADHOC_LIGHT_CSV="$ADHOC_DIR/pressure_adhoc_light.csv"

ADHOC_CMD="./semproxy --ex $EX --ey $EY --ez $EZ --dt $DT --timemax $TIMEMAX \
  --save-snapshots --snapshot-interval $INTERVAL --snapshot-folder snapshots"

cp "$BIN" "$ADHOC_DIR/semproxy"
echo "$ADHOC_CMD" > "$ADHOC_DIR/command_sim.txt"
( cd "$ADHOC_DIR" && bash -lc "$ADHOC_CMD" >/dev/null )

ADHOC_METRICS="$ADHOC_DIR/snapshot_metrics/metrics.json"
read -r ADHOC_COMP ADHOC_OUT ADHOC_BYTES < <(read_last_metrics "$ADHOC_METRICS")
ADHOC_TOTAL_SIM=$(python3 - <<PY
c=float("$ADHOC_COMP"); o=float("$ADHOC_OUT")
print(f"{c+o:.6f}")
PY
)

# postprocess time measured inside python (not in bash)
POST_TIME=$(python3 - <<PY
import time, subprocess, sys
cmd=["python3","postprocess_snapshots_light.py","--snapshots","$SNAPDIR","--out","$ADHOC_LIGHT_CSV","--dt","$DT"]
t0=time.time()
subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t1=time.time()
print(f"{t1-t0:.6f}")
PY
)

ADHOC_TOTAL_WITH_POST=$(python3 - <<PY
s=float("$ADHOC_TOTAL_SIM"); p=float("$POST_TIME")
print(f"{s+p:.6f}")
PY
)

echo "insitu_sim_total_s=$INSITU_TOTAL_SIM"
echo "adhoc_sim_total_s=$ADHOC_TOTAL_SIM"
echo "adhoc_post_s=$POST_TIME"
echo "adhoc_total_with_post_s=$ADHOC_TOTAL_WITH_POST"
echo "insitu_bytes=$INSITU_BYTES"
echo "adhoc_bytes=$ADHOC_BYTES"
echo "outdir=$OUTDIR"