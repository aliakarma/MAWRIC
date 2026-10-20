"""Run the MAWRIC-X study end to end.

    python run_all.py --smoke   # small run of every experiment (a few minutes)
    python run_all.py --full    # the runs reported in the paper plus the E3a checks (about an hour on 10 workers)

The full mode also regenerates manuscript/numbers.tex, manuscript/tabledefs.tex,
the figures and manuscript/references.bib. Compile the paper afterwards with
    cd manuscript && latexmk -pdf MAWRIC_X_Water.tex
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ("weather", [sys.executable, "-c", "from mawricx.weather import build_all; build_all()"]),
    ("E1 coordination", [sys.executable, "experiments/e1_coordination.py"]),
    ("E2 negotiation", [sys.executable, "experiments/e2_negotiation.py"]),
    ("E3a assurance", [sys.executable, "experiments/e3_assurance.py"]),
    ("E3b leak response", [sys.executable, "experiments/e3b_leak_response.py"]),
    ("E4 economics", [sys.executable, "experiments/e4_economics.py"]),
]


def main():
    smoke = "--smoke" in sys.argv
    if not smoke and "--full" not in sys.argv:
        sys.exit(__doc__)
    logs = ROOT / "results" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for name, cmd in STEPS:
        if smoke and name != "weather":
            cmd = cmd + ["--smoke"]
        tag = "smoke" if smoke else "full"
        log = logs / f"{name.split()[0].lower()}_{tag}.log"
        print(f"[{time.time() - t0:6.0f}s] {name} -> {log.relative_to(ROOT)}", flush=True)
        with open(log, "w", encoding="utf-8") as fh:
            subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, check=True)
    tag = "smoke" if smoke else "full"
    if not smoke:
        # E3a checks and post hoc analyses that make_results.py reads, then the manuscript inputs
        for script, extra in (("analysis/verify_e3a_serial.py", ["--every", "10", "--contexts",
                                                                 "1,3,4,6,7,8,18,19,25,28,81,87"]),
                              ("analysis/e3a_twin_misses.py", []), ("analysis/e3a_robust_twin.py", []),
                              ("analysis/make_results.py", []), ("analysis/build_bib.py", [])):
            print(f"[{time.time() - t0:6.0f}s] {script}", flush=True)
            args = [] if script.endswith("build_bib.py") else ["--tag", tag]
            subprocess.run([sys.executable, script, *args, *extra], cwd=ROOT, check=True)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
