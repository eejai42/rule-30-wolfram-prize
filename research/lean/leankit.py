"""Run Lean against the Rule 30 Prize kit: compile a module, check it with the kit's Check.lean, export it.

Everything runs inside the kit's own Lake environment (`lake env`, from external/Rule30PrizeKit), so the
kit, Mathlib and the toolchain are exactly the kit's. A module of ours (the ledger, a submission) is
compiled with `lean -o` into a directory of its own that is put in front of LEAN_PATH; the kit's checkout
stays untouched.
"""
from __future__ import annotations
import json, os, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / 'external' / 'Rule30PrizeKit'
KIT_URL = 'https://github.com/WolframInstitute/Rule30PrizeKit.git'
OUT = ROOT / 'lean' / '.out'
EXPORTER = ROOT / 'lean' / 'ExportKit.lean'


def lake() -> str | None:
    """The `lake` binary: on PATH, or where elan installs it."""
    found = shutil.which('lake')
    if found:
        return found
    elan = Path.home() / '.elan' / 'bin' / 'lake'
    return str(elan) if elan.exists() else None


def available() -> bool:
    return lake() is not None and (KIT / 'lakefile.toml').exists() and (KIT / '.lake').exists()


def _env(extra: Path | None) -> dict:
    env = dict(os.environ)
    env['PATH'] = f"{Path(lake()).parent}:{env.get('PATH', '')}"
    if extra:
        env['RULE30_EXTRA_LEAN_PATH'] = str(extra)
    return env


def run_lean(args: list[str], extra: Path | None = None, timeout: int = 3600) -> subprocess.CompletedProcess:
    """`lake env lean <args>` from the kit, with `extra` (a directory of our .olean files) first on LEAN_PATH."""
    inner = 'LEAN_PATH="${RULE30_EXTRA_LEAN_PATH:+$RULE30_EXTRA_LEAN_PATH:}$LEAN_PATH" exec lean "$@"'
    return subprocess.run([lake(), 'env', 'bash', '-c', inner, 'lean', *args], cwd=KIT, env=_env(extra),
                          capture_output=True, text=True, timeout=timeout)


def compile_module(source: Path, module: str, outdir: Path) -> tuple[bool, str]:
    """Compile `source` as module `module`, writing outdir/<module path>.olean. Returns (ok, messages)."""
    rel = Path(*module.split('.'))
    olean = outdir / rel.with_suffix('.olean')
    olean.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ('.olean', '.ilean', '.olean.server', '.olean.private'):
        p = olean.with_name(olean.stem + suffix)
        if p.exists():
            p.unlink()
    # Lean names the module after the file's path under --root, so the source sits there under its module path.
    placed = outdir / rel.with_suffix('.lean')
    if source.resolve() != placed.resolve():
        placed.write_bytes(source.read_bytes())
    proc = run_lean([str(placed), f'--root={outdir}', '-o', str(olean), '-i', str(olean.with_suffix('.ilean'))], extra=outdir)
    return proc.returncode == 0, (proc.stdout + proc.stderr)


def check(module: str, headlines: list[str], outdir: Path, claim: str = 'partial') -> dict:
    """The kit's Check.lean, exactly as the verifier runs it, on a compiled module of ours."""
    args = ['--run', 'Check.lean', module, '--claim', claim]
    for h in headlines:
        args += ['--headline', h]
    proc = run_lean(args, extra=outdir)
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {'verdict': 'error', 'reasons': [(proc.stdout + proc.stderr)[-2000:]]}


def export(out: Path, imports: list[str] | None = None, prefixes: list[str] | None = None, extra: Path | None = None) -> str:
    """lean/ExportKit.lean: the declarations of the kit (or of the modules under `prefixes`) as JSON."""
    args = ['--run', str(EXPORTER), str(out)] + [f'--prefix={p}' for p in (prefixes or [])] + list(imports or [])
    proc = run_lean(args, extra=extra)
    if proc.returncode != 0:
        raise RuntimeError(f'ExportKit failed: {(proc.stdout + proc.stderr)[-3000:]}')
    return proc.stdout.strip()


def build_kit(log: Path) -> tuple[bool, str]:
    """The kit's own build_all.sh (prebuilt Mathlib, then every catalog module, one at a time)."""
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('w') as fh:
        proc = subprocess.run(['bash', 'build_all.sh', '-k'], cwd=KIT, env=_env(None), stdout=fh, stderr=subprocess.STDOUT)
    tail = log.read_text().splitlines()[-3:]
    return proc.returncode == 0, '\n'.join(tail)
