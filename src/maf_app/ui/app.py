"""Streamlit UI for GOVAIAPP-MAF -- AI Governance Policy Generator."""

import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from dotenv import load_dotenv
import httpx
import streamlit as st

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

_MATURITE_LABELS: dict[str, str] = {
    "debutant": "\U0001f7e1 Debutant",
    "intermediaire": "\U0001f7e0 Intermediaire",
    "avance": "\U0001f7e2 Avance",
}

_AGENT_STEPS = [
    ("veille_externe", "\U0001f310 Veille Externe", "Analyse des signaux reglementaires..."),
    ("rag_interne", "\U0001f4da RAG Interne", "Recherche dans la base documentaire..."),
    ("producteur_politique", "\U0001f4dd Producteur Politique", "Redaction de la politique..."),
]

_STATUS_ICONS: dict[str, str] = {
    "queued": "\u23f3",
    "running": "\u2699\ufe0f",
    "done": "\u2705",
    "failed": "\u274c",
    "fallback": "\u26a0\ufe0f",
}

_EST_SECONDS = {"stub": [0.3, 0.3, 0.4], "foundry": [20.0, 25.0, 30.0]}


# ---------------------------------------------------------------------------
# Pure helpers (importable / testable)
# ---------------------------------------------------------------------------

def parse_principes(text: str) -> list[str]:
    """Convert multiline text to list of non-empty principles."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def call_generate_policy(
    payload: dict[str, Any],
    base_url: str = API_URL,
) -> dict[str, Any]:
    """POST /generate-policy and return JSON or raise."""
    url = f"{base_url}/generate-policy"
    response = httpx.post(url, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    return f"{seconds:.1f}s"


# ---------------------------------------------------------------------------
# Page config + CSS
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="GOVAIAPP-MAF | Gouvernance IA",
    page_icon="\U0001f3db\ufe0f",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem; border-radius: 12px;
        margin-bottom: 1.5rem; color: white;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; color: white; }
    .main-header p {
        margin: 0.3rem 0 0 0; opacity: 0.85; font-size: 0.95rem; color: #e0e0e0;
    }
    .mode-badge {
        display: inline-block; padding: 0.25rem 0.75rem;
        border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    }
    .mode-foundry { background:#0f3460; color:#53d8fb; border:1px solid #53d8fb; }
    .mode-stub   { background:#2d2d2d; color:#ffc107; border:1px solid #ffc107; }
    .pipeline-step {
        padding: 0.5rem 0.75rem; border-left: 3px solid #444;
        margin-bottom: 0.5rem; border-radius: 0 6px 6px 0;
        background: rgba(255,255,255,0.03);
    }
    .pipeline-step.done     { border-left-color: #4caf50; }
    .pipeline-step.failed   { border-left-color: #f44336; }
    .pipeline-step.fallback { border-left-color: #ff9800; }
    .pipeline-step.running  { border-left-color: #2196f3; }
    .step-header { font-weight: 600; font-size: 0.9rem; }
    .step-meta   { font-size: 0.75rem; opacity: 0.7; }
    div[data-testid="stForm"] {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px; padding: 1rem;
    }
    .metric-card {
        text-align: center; padding: 0.6rem 0.3rem;
        border-radius: 8px; background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .metric-card .value {
        font-size: 1.4rem; font-weight: 700; color: #53d8fb;
    }
    .metric-card .label {
        font-size: 0.7rem; opacity: 0.6; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# -- Session state --
if "result_data" not in st.session_state:
    st.session_state.result_data = None
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None

_foundry_on = os.getenv("FOUNDRY_ENABLED", "false").lower() == "true"
_mode_label = "Azure AI Foundry" if _foundry_on else "Stub local"
_mode_class = "mode-foundry" if _foundry_on else "mode-stub"
_mode_key = "foundry" if _foundry_on else "stub"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <h1>\U0001f3db\ufe0f GOVAIAPP-MAF</h1>
    <p>Generateur de politiques de gouvernance IA &mdash; Microsoft Agent Framework</p>
    <div style="margin-top:0.5rem;">
        <span class="mode-badge {_mode_class}">{_mode_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([2, 3], gap="large")

# ===== LEFT COLUMN =====
with col_left:
    st.subheader("\U0001f4cb Contexte entreprise")
    with st.form("policy_form"):
        nom = st.text_input("Nom de l'entreprise *", placeholder="Ex : Acme Corp")
        secteur = st.text_input(
            "Secteur d'activite *", placeholder="Ex : Finance, Sante, TI..."
        )
        maturite_donnees = st.selectbox(
            "Maturite donnees *",
            options=list(_MATURITE_LABELS.keys()),
            format_func=_MATURITE_LABELS.__getitem__,
        )
        principes_raw = st.text_area(
            "Principes directeurs (un par ligne)",
            placeholder="Transparence\nResponsabilite\nEquite",
            height=100,
        )
        contraintes = st.text_area(
            "Contraintes specifiques",
            placeholder="Conformite RGPD, pas de LLM cloud...",
            height=70,
        )
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            submitted = st.form_submit_button(
                "\u25b6 Generer", use_container_width=True
            )
        with col_b2:
            reset = st.form_submit_button(
                "\U0001f504 Reset", use_container_width=True
            )

    if reset:
        st.session_state.result_data = None
        st.session_state.error_msg = None
        st.rerun()


# ---------------------------------------------------------------------------
# Pipeline helpers
# ---------------------------------------------------------------------------

def _render_pipeline_step_html(
    label: str, status: str, duration: float = 0.0, fallback: str = ""
) -> str:
    icon = _STATUS_ICONS.get(status, "\u2753")
    meta = f"{status.upper()}"
    if status in ("done", "fallback", "failed"):
        meta += f" \u2014 {format_duration(duration)}"
    if fallback:
        meta += f"  |  {fallback}"
    return (
        f'<div class="pipeline-step {status}">'
        f'<span class="step-header">{icon} {label}</span><br>'
        f'<span class="step-meta">{meta}</span></div>'
    )


def _render_pipeline_panel(result_data: dict[str, Any] | None) -> None:
    st.markdown("---")
    st.subheader("\U0001f916 Agent Pipeline")
    if result_data and "steps" in result_data:
        for step in result_data["steps"]:
            agent_key = step["agent"]
            label = dict((k, l) for k, l, _ in _AGENT_STEPS).get(agent_key, agent_key)
            st.markdown(
                _render_pipeline_step_html(
                    label, step["status"],
                    step.get("duration_s", 0),
                    step.get("fallback_reason", ""),
                ),
                unsafe_allow_html=True,
            )
        total = result_data.get("duration_s", 0)
        mode = result_data.get("mode_used", "?")
        st.caption(f"Total : {format_duration(total)} | Mode : {mode}")
    else:
        for _, label, _ in _AGENT_STEPS:
            st.markdown(
                _render_pipeline_step_html(label, "queued"),
                unsafe_allow_html=True,
            )
        st.caption("En attente de lancement...")


# ===== RIGHT COLUMN =====
with col_right:
    st.subheader("\U0001f4c4 Politique generee")

    if submitted:
        if not nom.strip() or not secteur.strip():
            st.session_state.error_msg = "Le nom et le secteur sont obligatoires."
            st.session_state.result_data = None
        else:
            st.session_state.error_msg = None
            payload = {
                "company_name": nom.strip(),
                "sector": secteur.strip(),
                "maturite_donnees": maturite_donnees,
                "principles": parse_principes(principes_raw),
                "constraints": (
                    [contraintes.strip()] if contraintes.strip() else []
                ),
            }

            # --- Animated pipeline ---
            pipeline_placeholder = col_left.empty()
            est = _EST_SECONDS[_mode_key]

            with ThreadPoolExecutor(max_workers=1) as pool:
                future: Future[dict[str, Any]] = pool.submit(
                    call_generate_policy, payload
                )
                t_start = time.monotonic()
                cumulative_est = [sum(est[: i + 1]) for i in range(len(est))]
                total_est = cumulative_est[-1]

                while not future.done():
                    elapsed = time.monotonic() - t_start
                    current_step = 0
                    for i, threshold in enumerate(cumulative_est):
                        if elapsed < threshold:
                            current_step = i
                            break
                    else:
                        current_step = len(est) - 1

                    html_parts = ["<hr>", "<h4>\U0001f916 Agent Pipeline</h4>"]
                    for i, (key, label, desc) in enumerate(_AGENT_STEPS):
                        if i < current_step:
                            html_parts.append(
                                _render_pipeline_step_html(label, "done", duration=est[i])
                            )
                        elif i == current_step:
                            step_elapsed = elapsed - (cumulative_est[i - 1] if i > 0 else 0)
                            html_parts.append(
                                f'<div class="pipeline-step running">'
                                f'<span class="step-header">\u2699\ufe0f {label}</span><br>'
                                f'<span class="step-meta">EN COURS \u2014 '
                                f'{format_duration(step_elapsed)}'
                                f' &nbsp; <em>{desc}</em></span></div>'
                            )
                        else:
                            html_parts.append(
                                _render_pipeline_step_html(label, "queued")
                            )

                    pct = min(elapsed / total_est, 0.99) if total_est > 0 else 0
                    html_parts.append(
                        f'<p style="font-size:0.8rem;opacity:0.6;">'
                        f'Progression estimee : {pct:.0%} '
                        f'({format_duration(elapsed)})</p>'
                    )
                    pipeline_placeholder.markdown(
                        "\n".join(html_parts), unsafe_allow_html=True
                    )
                    time.sleep(0.5)

                pipeline_placeholder.empty()
                try:
                    data = future.result()
                    st.session_state.result_data = data
                    st.session_state.error_msg = None
                    st.rerun()
                except httpx.ConnectError:
                    st.session_state.error_msg = (
                        "Impossible de joindre l'API. "
                        "Verifiez que le serveur FastAPI est lance."
                    )
                    st.session_state.result_data = None
                except httpx.TimeoutException:
                    st.session_state.error_msg = (
                        "L'API n'a pas repondu dans les 180 secondes."
                    )
                    st.session_state.result_data = None
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 422:
                        st.session_state.error_msg = (
                            f"Donnees invalides (422) : {exc.response.text}"
                        )
                    else:
                        st.session_state.error_msg = (
                            f"Erreur API ({exc.response.status_code})"
                        )
                    st.session_state.result_data = None
                except Exception as exc:
                    st.session_state.error_msg = f"Erreur inattendue : {exc!r}"
                    st.session_state.result_data = None

    # -- Error display --
    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)

    # -- Result display --
    if st.session_state.result_data:
        data = st.session_state.result_data
        mode = data.get("mode_used", "stub")
        duration = data.get("duration_s", 0)
        policy_md = data.get("policy_markdown", "")
        sources = data.get("sources", [])
        steps = data.get("steps", [])

        # --- Metrics row ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="value">{format_duration(duration)}</div>'
                f'<div class="label">Duree totale</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="value">{len(policy_md):,}</div>'
                f'<div class="label">Caracteres</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="value">{len(steps)}</div>'
                f'<div class="label">Agents</div></div>',
                unsafe_allow_html=True,
            )
        with m4:
            mode_icon = "\U0001f680" if mode == "foundry" else "\U0001f9ea"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="value">{mode_icon}</div>'
                f'<div class="label">{mode.upper()}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        # --- Tabs: Politique / Sources / Diagnostics ---
        tab_policy, tab_sources, tab_diag = st.tabs(
            ["\U0001f4c4 Politique", "\U0001f4da Sources", "\U0001f50d Diagnostics"]
        )

        with tab_policy:
            if policy_md:
                st.markdown(policy_md)
            else:
                st.warning("La reponse ne contient pas de politique.")

        with tab_sources:
            if sources:
                for src in sources:
                    agent_label = dict((k, l) for k, l, _ in _AGENT_STEPS).get(
                        src.get("source", ""), src.get("title", "N/A")
                    )
                    with st.expander(f"{agent_label}", expanded=False):
                        st.markdown(src.get("content", ""))
            else:
                st.info("Aucune source intermediaire disponible.")

        with tab_diag:
            # Step-by-step timing
            st.markdown("**Execution par agent :**")
            for step in steps:
                agent_key = step["agent"]
                label = dict((k, l) for k, l, _ in _AGENT_STEPS).get(
                    agent_key, agent_key
                )
                status = step["status"]
                dur = step.get("duration_s", 0)
                icon = _STATUS_ICONS.get(status, "")
                cols_d = st.columns([3, 1, 1])
                cols_d[0].markdown(f"{icon} **{label}**")
                cols_d[1].code(status.upper(), language=None)
                cols_d[2].markdown(f"`{format_duration(dur)}`")
                if step.get("fallback_reason"):
                    st.caption(f"\u26a0\ufe0f Fallback : {step['fallback_reason']}")

            st.markdown("---")
            st.markdown(
                f"**Total** : {format_duration(duration)} | "
                f"**Mode** : {mode} | "
                f"**Agents** : {len(steps)}"
            )

            fallbacks = [s for s in steps if s.get("status") == "fallback"]
            if fallbacks:
                st.warning(
                    f"{len(fallbacks)} agent(s) en fallback. "
                    "Voir les raisons ci-dessus."
                )
            failures = [s for s in steps if s.get("status") == "failed"]
            if failures:
                st.error(
                    f"{len(failures)} agent(s) en echec. "
                    "La politique peut etre incomplete."
                )

    elif not st.session_state.error_msg and not submitted:
        st.info(
            "\u2190 Remplissez le formulaire et cliquez sur "
            "**Generer** pour lancer le pipeline."
        )

# -- Static pipeline panel --
with col_left:
    if not submitted:
        _render_pipeline_panel(st.session_state.result_data)
