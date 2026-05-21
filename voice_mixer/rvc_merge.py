"""
Merge 2-3 trained RVC v2 .pth checkpoints into a single .pth via weighted
average of their weights. Output is loadable by w-okada/voice-changer or by
RVC's own inference, so you can take a mix you like in the offline mixer
and "bake" it into a single model for real-time use.

CLI:
    python rvc_merge.py \\
        --model rvc/models/herzog.pth:0.1 \\
        --model rvc/models/attenborough.pth:0.9 \\
        --output rvc/models/herzog-attenborough.pth \\
        --info "10% herzog + 90% attenborough"

Caveats:
- All inputs must share sample rate, f0 flag, and RVC version.
- Index files (.index) cannot be merged meaningfully. Use the merged model
  with index_rate=0, or copy one of the source .index files if you want
  some retrieval bias from a single contributor.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import torch


def merge_rvc_models(
    model_paths: list[Path],
    weights: list[float],
    output_path: Path,
    info: str = "",
) -> Path:
    if len(model_paths) != len(weights):
        raise ValueError("model_paths and weights must be the same length")
    if len(model_paths) < 2:
        raise ValueError("Need at least 2 models to merge")

    total = sum(weights)
    if total <= 0:
        raise ValueError("Weights must sum to > 0")
    weights = [w / total for w in weights]

    ckpts = [
        torch.load(p, map_location="cpu", weights_only=False)
        for p in model_paths
    ]
    base = ckpts[0]

    for i, c in enumerate(ckpts[1:], 1):
        for field in ("sr", "f0", "version"):
            if c.get(field) != base.get(field):
                raise ValueError(
                    f"Model {i} {field}={c.get(field)!r} differs from model 0 "
                    f"{field}={base.get(field)!r}"
                )

    out_weights = OrderedDict()
    for k in base["weight"]:
        tensors = []
        for i, c in enumerate(ckpts):
            if k not in c["weight"]:
                raise ValueError(f"Key {k!r} missing from model {i}")
            tensors.append(c["weight"][k].float())
        # RVC quirk: some layer shapes differ slightly across models trained
        # with different sample-rate options. Min-trim along dim 0 matches
        # what RVC's own ckpt-merge does.
        shapes = {t.shape for t in tensors}
        if len(shapes) > 1:
            try:
                min_d0 = min(t.shape[0] for t in tensors)
                tensors = [t[:min_d0] for t in tensors]
            except (IndexError, ValueError) as e:
                raise ValueError(
                    f"Incompatible shapes for key {k!r}: {shapes}"
                ) from e
        out_weights[k] = sum(w * t for w, t in zip(weights, tensors))

    opt = {
        "weight": out_weights,
        "config": base["config"],
        "sr": base["sr"],
        "f0": base["f0"],
        "version": base.get("version", "v2"),
        "info": info or f"merged from {len(ckpts)} models",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(opt, output_path)
    return output_path


def _parse_model_arg(s: str) -> tuple[Path, float]:
    if ":" not in s:
        raise argparse.ArgumentTypeError(
            f"Expected PATH:WEIGHT, got {s!r}"
        )
    path_str, weight_str = s.rsplit(":", 1)
    return Path(path_str), float(weight_str)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--model", "-m",
        action="append", required=True, type=_parse_model_arg,
        help="PATH:WEIGHT (use 2-3 times)",
    )
    ap.add_argument("--output", "-o", required=True, type=Path)
    ap.add_argument("--info", default="")
    args = ap.parse_args()

    paths = [p for p, _ in args.model]
    weights = [w for _, w in args.model]
    out = merge_rvc_models(paths, weights, args.output, info=args.info)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
