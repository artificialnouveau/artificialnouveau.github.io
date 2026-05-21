"""
OpenVoice v2 voice mixer.

Two tabs:
  Mixer   - blend up to 3 target voices, optional RVC post-pass.
            Two modes:
              Voice conversion: input audio is re-coloured by the mixed voice.
              Text-to-speech  : MeloTTS speaks typed text in the mixed voice.
  Profiles - build named voice profiles from multiple reference clips,
             saved as averaged embeddings in voice_mixer/voices/.

Mixing math:
  Linear  : mixed = sum(w_i * se_i), weights normalized to sum to 1.
  Spherical: true slerp for 2 voices, norm-preserving weighted mean (nlerp)
             for 3 voices, no-op for 1.

RVC post-pass:
  Optional. Requires rvc-python (pip install -r requirements-rvc.txt) and at
  least one trained .pth in voice_mixer/rvc/models/.
"""
from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr
import torch

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS

from rvc_merge import merge_rvc_models

ROOT = Path(__file__).parent
CKPT = ROOT / "checkpoints_v2"
VOICES_DIR = ROOT / "voices"
VOICES_DIR.mkdir(exist_ok=True)
RVC_MODELS_DIR = ROOT / "rvc" / "models"

if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

LANGUAGES = {
    "English": ("EN", "EN-Default", "en-default"),
    "Spanish": ("ES", "ES", "es"),
    "French": ("FR", "FR", "fr"),
    "Chinese": ("ZH", "ZH", "zh"),
    "Japanese": ("JP", "JP", "jp"),
    "Korean": ("KR", "KR", "kr"),
}

NO_PROFILE = "(use upload below)"

print(f"Loading tone color converter on {DEVICE}...")
converter = ToneColorConverter(
    str(CKPT / "converter" / "config.json"), device=DEVICE
)
converter.load_ckpt(str(CKPT / "converter" / "checkpoint.pth"))

_tts_cache: dict[str, TTS] = {}


def get_tts(lang_code: str) -> TTS:
    if lang_code not in _tts_cache:
        _tts_cache[lang_code] = TTS(language=lang_code, device=DEVICE)
    return _tts_cache[lang_code]


def extract_se(audio_path: str | None):
    if not audio_path:
        return None
    with tempfile.TemporaryDirectory() as td:
        se, _ = se_extractor.get_se(
            audio_path, converter, target_dir=td, vad=True
        )
    return se


# ---------- profile management ----------

def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "voice"


def save_profile(name: str, embedding, n_clips: int, language: str) -> Path:
    slug = slugify(name)
    path = VOICES_DIR / f"{slug}.pt"
    torch.save(
        {
            "name": name.strip(),
            "embedding": embedding.detach().cpu(),
            "n_clips": n_clips,
            "language": language,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        path,
    )
    return path


def list_profiles() -> list[dict]:
    out = []
    for p in sorted(VOICES_DIR.glob("*.pt")):
        try:
            d = torch.load(p, map_location="cpu", weights_only=False)
            out.append(
                {
                    "slug": p.stem,
                    "name": d.get("name", p.stem),
                    "n_clips": d.get("n_clips", 1),
                    "language": d.get("language", ""),
                    "created_at": d.get("created_at", ""),
                }
            )
        except Exception as e:
            print(f"Skipping malformed profile {p}: {e}")
    return out


def profile_choices() -> list[str]:
    return [NO_PROFILE] + [p["name"] for p in list_profiles()]


def slug_for_name(name: str) -> str | None:
    if not name or name == NO_PROFILE:
        return None
    for p in list_profiles():
        if p["name"] == name:
            return p["slug"]
    return None


def load_profile_embedding(name: str | None):
    slug = slug_for_name(name)
    if slug is None:
        return None
    path = VOICES_DIR / f"{slug}.pt"
    if not path.exists():
        return None
    d = torch.load(path, map_location=DEVICE, weights_only=False)
    return d["embedding"].to(DEVICE)


def build_profile(name: str, files, language: str):
    if not name or not name.strip():
        raise gr.Error("Give the profile a name.")
    if not files:
        raise gr.Error("Upload at least one audio clip.")

    paths = [f.name if hasattr(f, "name") else f for f in files]
    embeddings = []
    for p in paths:
        try:
            se = extract_se(p)
            if se is not None:
                embeddings.append(se)
        except Exception as e:
            print(f"Failed to extract from {p}: {e}")

    if not embeddings:
        raise gr.Error("Could not extract any embeddings from those clips.")

    avg = torch.stack(embeddings).mean(dim=0)
    save_profile(name, avg, len(embeddings), language)

    status = f"Saved profile '{name.strip()}' from {len(embeddings)} clip(s)."
    return status, profiles_table(), gr.update(choices=profile_choices())


def delete_profile_action(name: str):
    slug = slug_for_name(name)
    if slug is None:
        return "Nothing to delete.", profiles_table(), gr.update(choices=profile_choices())
    path = VOICES_DIR / f"{slug}.pt"
    path.unlink(missing_ok=True)
    return f"Deleted '{name}'.", profiles_table(), gr.update(choices=profile_choices())


def profiles_table():
    rows = list_profiles()
    if not rows:
        return [["(no profiles yet)", "", "", ""]]
    return [
        [r["name"], str(r["n_clips"]), r["language"], r["created_at"]]
        for r in rows
    ]


# ---------- RVC post-pass ----------

def list_rvc_models() -> list[str]:
    if not RVC_MODELS_DIR.exists():
        return []
    return sorted(p.stem for p in RVC_MODELS_DIR.glob("*.pth"))


_rvc_cache: dict = {}


def apply_rvc(input_wav: str, model_name: str, transpose: int, index_rate: float) -> str:
    try:
        from rvc_python.infer import RVCInference
    except ImportError as e:
        raise gr.Error(
            "rvc-python not installed. Run: pip install -r requirements-rvc.txt"
        ) from e

    rvc_device = DEVICE if DEVICE != "mps" else "cpu"
    if model_name not in _rvc_cache:
        rvc = RVCInference(device=rvc_device)
        model_path = RVC_MODELS_DIR / f"{model_name}.pth"
        rvc.load_model(str(model_path))
        _rvc_cache[model_name] = rvc
    rvc = _rvc_cache[model_name]

    try:
        rvc.set_params(f0up_key=int(transpose), index_rate=float(index_rate))
    except TypeError:
        # Older versions used different kwarg names; let it fall through.
        rvc.set_params(f0up_key=int(transpose))

    out_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    rvc.infer_file(input_wav, out_path)
    return out_path


# ---------- mixing ----------

def blend_embeddings(weighted_ses, spherical: bool):
    if len(weighted_ses) == 1:
        return weighted_ses[0][0]

    if spherical and len(weighted_ses) == 2:
        (se0, _), (se1, w1) = weighted_ses
        t = w1
        n0 = se0 / (se0.norm() + 1e-9)
        n1 = se1 / (se1.norm() + 1e-9)
        dot = (n0 * n1).sum().clamp(-1.0, 1.0)
        omega = torch.acos(dot)
        if omega.abs() < 1e-6:
            return (1 - t) * se0 + t * se1
        sin_omega = torch.sin(omega)
        return (
            torch.sin((1 - t) * omega) / sin_omega * se0
            + torch.sin(t * omega) / sin_omega * se1
        )

    mixed = sum(w * se for se, w in weighted_ses)
    if spherical:
        target_norm = sum(w * se.norm() for se, w in weighted_ses)
        current = mixed.norm()
        if current > 1e-9:
            mixed = mixed * (target_norm / current)
    return mixed


def resolve_se(profile_name, ref_audio, cached_state):
    """Profile dropdown wins; otherwise upload; otherwise cached."""
    if profile_name and profile_name != NO_PROFILE:
        return load_profile_embedding(profile_name)
    if cached_state is not None:
        return cached_state
    if ref_audio is not None:
        return extract_se(ref_audio)
    return None


def mix(
    mode,
    source_audio,
    prof_a, prof_b, prof_c,
    ref_a, ref_b, ref_c,
    w_a, w_b, w_c,
    text, language, speed, spherical,
    rvc_enabled, rvc_model, rvc_transpose, rvc_index_rate,
    se_a_state, se_b_state, se_c_state, source_se_state,
):
    if mode == "Voice conversion":
        if not source_audio:
            raise gr.Error("Upload or record source audio to convert.")
    else:
        if not text or not text.strip():
            raise gr.Error("Please enter some text to speak.")

    se_a = resolve_se(prof_a, ref_a, se_a_state)
    se_b = resolve_se(prof_b, ref_b, se_b_state)
    se_c = resolve_se(prof_c, ref_c, se_c_state)

    if prof_a == NO_PROFILE:
        se_a_state = se_a
    if prof_b == NO_PROFILE:
        se_b_state = se_b
    if prof_c == NO_PROFILE:
        se_c_state = se_c

    slots = [("A", se_a, w_a), ("B", se_b, w_b), ("C", se_c, w_c)]
    active = [(name, se, w) for name, se, w in slots if se is not None and w > 0]
    if not active:
        raise gr.Error(
            "Provide at least one voice (profile or upload) with weight > 0."
        )

    total = sum(w for _, _, w in active)
    weighted = [(se, w / total) for _, se, w in active]
    mixed_se = blend_embeddings(weighted, spherical=spherical)

    out_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

    if mode == "Voice conversion":
        # The user's own audio is the source; extract its SE so the converter
        # knows what tone color it's converting *from*.
        if source_se_state is None:
            source_se_state = extract_se(source_audio)
        if source_se_state is None:
            raise gr.Error("Could not extract a speaker embedding from the source audio.")
        converter.convert(
            audio_src_path=source_audio,
            src_se=source_se_state,
            tgt_se=mixed_se,
            output_path=out_path,
        )
        cleanup_src = None
    else:
        # TTS path: synthesize text with MeloTTS, then re-color it.
        lang_code, melo_speaker, base_se_name = LANGUAGES[language]
        tts = get_tts(lang_code)
        speaker_ids = tts.hps.data.spk2id
        if melo_speaker not in speaker_ids:
            melo_speaker = next(iter(speaker_ids))
        src_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        tts.tts_to_file(text, speaker_ids[melo_speaker], src_path, speed=speed)
        source_se = torch.load(
            CKPT / "base_speakers" / "ses" / f"{base_se_name}.pth",
            map_location=DEVICE,
        )
        converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=mixed_se,
            output_path=out_path,
        )
        cleanup_src = src_path

    if cleanup_src:
        try:
            os.unlink(cleanup_src)
        except OSError:
            pass

    final_path = out_path
    if rvc_enabled and rvc_model:
        final_path = apply_rvc(out_path, rvc_model, rvc_transpose, rvc_index_rate)

    parts = [f"{w / total * 100:.0f}% {name}" for name, _, w in active]
    label = " + ".join(parts)
    if spherical:
        label += f"  ({'slerp' if len(active) == 2 else 'nlerp'})"
    if mode == "Voice conversion":
        label = f"VC: {label}"
    if rvc_enabled and rvc_model:
        label += f"  + RVC[{rvc_model}]"
    return final_path, se_a_state, se_b_state, se_c_state, source_se_state, label


def invalidate(_):
    return None


# ---------- UI ----------

with gr.Blocks(title="Voice Mixer (OpenVoice v2)") as demo:
    gr.Markdown("# Voice Mixer")

    with gr.Tabs():

        # ===== Mixer tab =====
        with gr.Tab("Mixer"):
            gr.Markdown(
                "Pick a mode, then set up to three target voices (profile or "
                "upload) with weights. Weights are normalized to 100%."
            )

            mode = gr.Radio(
                ["Voice conversion", "Text-to-speech"],
                value="Voice conversion",
                label="Mode",
                info=(
                    "Voice conversion: your input audio gets re-coloured by "
                    "the mixed voice. Text-to-speech: type text, MeloTTS "
                    "speaks it in the mixed voice."
                ),
            )

            source_audio = gr.Audio(
                label="Source audio (your speech)",
                type="filepath",
                sources=["upload", "microphone"],
                visible=True,
            )

            initial_profiles = profile_choices()

            with gr.Row():
                with gr.Column():
                    prof_a = gr.Dropdown(
                        initial_profiles, value=NO_PROFILE, label="Profile A"
                    )
                    ref_a = gr.Audio(
                        label="Or upload reference A",
                        type="filepath",
                        sources=["upload", "microphone"],
                    )
                    w_a = gr.Slider(0, 100, value=50, step=1, label="Weight A")
                with gr.Column():
                    prof_b = gr.Dropdown(
                        initial_profiles, value=NO_PROFILE, label="Profile B"
                    )
                    ref_b = gr.Audio(
                        label="Or upload reference B",
                        type="filepath",
                        sources=["upload", "microphone"],
                    )
                    w_b = gr.Slider(0, 100, value=50, step=1, label="Weight B")
                with gr.Column():
                    prof_c = gr.Dropdown(
                        initial_profiles, value=NO_PROFILE, label="Profile C"
                    )
                    ref_c = gr.Audio(
                        label="Or upload reference C (optional)",
                        type="filepath",
                        sources=["upload", "microphone"],
                    )
                    w_c = gr.Slider(0, 100, value=0, step=1, label="Weight C")

            with gr.Row():
                language = gr.Dropdown(
                    list(LANGUAGES.keys()), value="English",
                    label="Language", visible=False,
                )
                speed = gr.Slider(
                    0.5, 2.0, value=1.0, step=0.05, label="Speed",
                    visible=False,
                )
                spherical = gr.Checkbox(
                    value=False,
                    label="Spherical interpolation (slerp / nlerp)",
                )

            text = gr.Textbox(
                label="Text to speak",
                lines=3,
                placeholder="Type what the mixed voice should say.",
                visible=False,
            )

            with gr.Accordion("RVC post-pass (optional)", open=False):
                rvc_models = list_rvc_models()
                rvc_enabled = gr.Checkbox(
                    value=False,
                    label="Apply RVC after mixing",
                    interactive=bool(rvc_models),
                )
                rvc_model = gr.Dropdown(
                    rvc_models or ["(no models found)"],
                    value=(rvc_models[0] if rvc_models else "(no models found)"),
                    label="RVC model",
                    interactive=bool(rvc_models),
                )
                with gr.Row():
                    rvc_transpose = gr.Slider(
                        -12, 12, value=0, step=1,
                        label="Transpose (semitones)",
                    )
                    rvc_index_rate = gr.Slider(
                        0.0, 1.0, value=0.66, step=0.01,
                        label="Index rate",
                    )
                rvc_refresh = gr.Button("Rescan rvc/models/", size="sm")

            generate = gr.Button("Generate", variant="primary")

            output_audio = gr.Audio(label="Output", type="filepath")
            output_label = gr.Markdown()

            se_a_state = gr.State()
            se_b_state = gr.State()
            se_c_state = gr.State()
            source_se_state = gr.State()

            ref_a.change(invalidate, ref_a, se_a_state)
            ref_b.change(invalidate, ref_b, se_b_state)
            ref_c.change(invalidate, ref_c, se_c_state)
            source_audio.change(invalidate, source_audio, source_se_state)

            def toggle_mode(m):
                vc = (m == "Voice conversion")
                return (
                    gr.update(visible=vc),       # source_audio
                    gr.update(visible=not vc),   # text
                    gr.update(visible=not vc),   # language
                    gr.update(visible=not vc),   # speed
                )

            mode.change(
                toggle_mode,
                inputs=[mode],
                outputs=[source_audio, text, language, speed],
            )

            def rescan_rvc():
                models = list_rvc_models()
                return gr.update(
                    choices=models or ["(no models found)"],
                    value=(models[0] if models else "(no models found)"),
                    interactive=bool(models),
                ), gr.update(interactive=bool(models))

            rvc_refresh.click(rescan_rvc, outputs=[rvc_model, rvc_enabled])

            generate.click(
                mix,
                inputs=[
                    mode, source_audio,
                    prof_a, prof_b, prof_c,
                    ref_a, ref_b, ref_c,
                    w_a, w_b, w_c,
                    text, language, speed, spherical,
                    rvc_enabled, rvc_model, rvc_transpose, rvc_index_rate,
                    se_a_state, se_b_state, se_c_state, source_se_state,
                ],
                outputs=[
                    output_audio,
                    se_a_state, se_b_state, se_c_state, source_se_state,
                    output_label,
                ],
            )

        # ===== Profiles tab =====
        with gr.Tab("Voice Profiles"):
            gr.Markdown(
                "Build a named voice profile by averaging embeddings from "
                "multiple clips of the same speaker (more clips = more stable "
                "embedding). Saved to `voice_mixer/voices/`."
            )

            with gr.Row():
                profile_name = gr.Textbox(
                    label="Profile name",
                    placeholder="e.g. werner-herzog",
                )
                profile_lang = gr.Dropdown(
                    list(LANGUAGES.keys()),
                    value="English",
                    label="Primary language (metadata only)",
                )

            profile_files = gr.File(
                label="Reference clips (5-30s each, mono, clean)",
                file_count="multiple",
                file_types=["audio"],
            )

            with gr.Row():
                build_btn = gr.Button("Build profile", variant="primary")
                delete_target = gr.Dropdown(
                    [p["name"] for p in list_profiles()],
                    label="Delete profile",
                )
                delete_btn = gr.Button("Delete")

            profile_status = gr.Markdown()

            profiles_view = gr.Dataframe(
                headers=["Name", "Clips", "Language", "Created (UTC)"],
                value=profiles_table(),
                interactive=False,
                label="Saved profiles",
            )

            def refresh_profile_dropdowns():
                choices = profile_choices()
                names_only = [c for c in choices if c != NO_PROFILE]
                return (
                    gr.update(choices=choices),
                    gr.update(choices=choices),
                    gr.update(choices=choices),
                    gr.update(choices=names_only),
                )

            def build_and_refresh(name, files, lang):
                status, table, _ = build_profile(name, files, lang)
                a, b, c, d = refresh_profile_dropdowns()
                return status, table, a, b, c, d

            def delete_and_refresh(name):
                status, table, _ = delete_profile_action(name)
                a, b, c, d = refresh_profile_dropdowns()
                return status, table, a, b, c, d

            build_btn.click(
                build_and_refresh,
                inputs=[profile_name, profile_files, profile_lang],
                outputs=[
                    profile_status, profiles_view,
                    prof_a, prof_b, prof_c, delete_target,
                ],
            )
            delete_btn.click(
                delete_and_refresh,
                inputs=[delete_target],
                outputs=[
                    profile_status, profiles_view,
                    prof_a, prof_b, prof_c, delete_target,
                ],
            )

        # ===== RVC Merge tab =====
        with gr.Tab("RVC Merge"):
            gr.Markdown(
                "Bake a mix into a single RVC model for **real-time use** in "
                "[w-okada/voice-changer](https://github.com/w-okada/voice-changer). "
                "Pick 2-3 trained models from `voice_mixer/rvc/models/`, set "
                "weights, name the output. The merged `.pth` lands back in "
                "the same folder.\n\n"
                "Workflow: audition mixes in the **Mixer** tab (instant, "
                "embedding-based), then come here to bake the ratio you like "
                "into a single model voice-changer can stream live. Note that "
                "all input models must share sample rate, f0 flag, and RVC "
                "version (true if you trained them in the same RVC version "
                "with the same options)."
            )

            initial_rvc = list_rvc_models()

            with gr.Row():
                merge_a = gr.Dropdown(
                    initial_rvc, label="Model A",
                    value=(initial_rvc[0] if initial_rvc else None),
                )
                merge_b = gr.Dropdown(
                    initial_rvc, label="Model B",
                    value=(initial_rvc[1] if len(initial_rvc) > 1 else None),
                )
                merge_c = gr.Dropdown(
                    [NO_PROFILE] + initial_rvc,
                    value=NO_PROFILE,
                    label="Model C (optional)",
                )

            with gr.Row():
                merge_w_a = gr.Slider(0, 100, value=50, step=1, label="Weight A")
                merge_w_b = gr.Slider(0, 100, value=50, step=1, label="Weight B")
                merge_w_c = gr.Slider(0, 100, value=0, step=1, label="Weight C")

            merge_name = gr.Textbox(
                label="Output model name",
                placeholder="e.g. herzog-attenborough-mix",
            )
            merge_btn = gr.Button("Merge", variant="primary")
            merge_status = gr.Markdown()

            def do_merge(a, b, c, wa, wb, wc, name):
                if not name or not name.strip():
                    raise gr.Error("Give the merged model a name.")
                slug = slugify(name)
                output_path = RVC_MODELS_DIR / f"{slug}.pth"
                if output_path.exists():
                    raise gr.Error(
                        f"{output_path.name} already exists. Pick a different name."
                    )

                picks = []
                if a:
                    picks.append((RVC_MODELS_DIR / f"{a}.pth", float(wa), a))
                if b:
                    picks.append((RVC_MODELS_DIR / f"{b}.pth", float(wb), b))
                if c and c != NO_PROFILE:
                    picks.append((RVC_MODELS_DIR / f"{c}.pth", float(wc), c))
                picks = [(p, w, n) for p, w, n in picks if w > 0]
                if len(picks) < 2:
                    raise gr.Error(
                        "Need at least 2 models with weight > 0."
                    )

                paths = [p for p, _, _ in picks]
                weights = [w for _, w, _ in picks]
                total = sum(weights)
                ratio_str = " + ".join(
                    f"{w / total * 100:.0f}% {n}" for _, w, n in picks
                )
                merge_rvc_models(
                    paths, weights, output_path, info=ratio_str,
                )

                models = list_rvc_models()
                return (
                    f"Wrote `rvc/models/{slug}.pth`  ({ratio_str}). "
                    "Click 'Rescan rvc/models/' in the Mixer tab to use it.",
                    gr.update(choices=models, value=models[0] if models else None),
                    gr.update(choices=models, value=models[1] if len(models) > 1 else None),
                    gr.update(choices=[NO_PROFILE] + models, value=NO_PROFILE),
                    gr.update(
                        choices=models or ["(no models found)"],
                        value=(models[0] if models else "(no models found)"),
                        interactive=bool(models),
                    ),
                    gr.update(interactive=bool(models)),
                )

            merge_btn.click(
                do_merge,
                inputs=[
                    merge_a, merge_b, merge_c,
                    merge_w_a, merge_w_b, merge_w_c,
                    merge_name,
                ],
                outputs=[
                    merge_status,
                    merge_a, merge_b, merge_c,
                    rvc_model, rvc_enabled,
                ],
            )


if __name__ == "__main__":
    demo.launch()
