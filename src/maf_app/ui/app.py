"""Streamlit UI for GOVAIAPP-MAF -- AI Governance Policy Generator."""

import os
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


def parse_principes(text: str) -> list[str]:
    """Convert multiline text to list of non-empty principles."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def call_generate_policy(
    payload: dict[str, Any],
    base_url: str = API_URL,
) -> dict[str, Any]:
    """POST /generate-policy and return JSON or raise."""
    url = f"{base_url}/generate-policy"
    response = httpx.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


# -- Page config --
st.set_page_config(
    page_title="GOVAIAPP-MAF - Gouvernance IA",
    page_icon="\U0001f916",
    layout="centered",
)
st.title("\U0001f916 GOVAIAPP-MAF -- Generateur de politique IA")
st.caption(
    "Renseignez le contexte de votre entreprise, "
    "puis cliquez sur **Generer la politique**."
)

# -- Mode indicator --
_foundry_on = os.getenv("FOUNDRY_ENABLED", "false").lower() == "true"
if _foundry_on:
    st.info("\U0001f680 Mode **Azure AI Foundry** actif")
else:
    st.info("\U0001f9ea Mode **Stub local** (FOUNDRY_ENABLED=false)")

# -- Form --
with st.form("policy_form"):
    nom = st.text_input("Nom de l'entreprise *", placeholder="Ex : Acme Corp")
    secteur = st.text_input(
        "Secteur d'activite *", placeholder="Ex : Finance, Sante, Industrie..."
    )
    maturite_donnees = st.selectbox(
        "Maturite donnees *",
        options=list(_MATURITE_LABELS.keys()),
        format_func=_MATURITE_LABELS.__getitem__,
    )
    principes_raw = st.text_area(
        "Principes directeurs (un par ligne)",
        placeholder="Transparence\nResponsabilite\nEquite",
        height=120,
    )
    contraintes = st.text_area(
        "Contraintes specifiques",
        placeholder="Ex : Conformite RGPD obligatoire, pas de LLM cloud...",
        height=80,
    )
    submitted = st.form_submit_button(
        "Generer la politique", use_container_width=True
    )

# -- Result --
if submitted:
    if not nom.strip() or not secteur.strip():
        st.warning("Le nom et le secteur sont obligatoires.")
    else:
        payload = {
            "company_name": nom.strip(),
            "sector": secteur.strip(),
            "maturite_donnees": maturite_donnees,
            "principles": parse_principes(principes_raw),
            "constraints": [contraintes.strip()] if contraintes.strip() else [],
        }

        with st.spinner("Generation en cours..."):
            try:
                data = call_generate_policy(payload)
            except httpx.ConnectError:
                st.error(
                    "Impossible de joindre l'API. "
                    "Verifiez que le serveur FastAPI est lance."
                )
                data = None
            except httpx.TimeoutException:
                st.error("L'API n'a pas repondu dans les 60 secondes.")
                data = None
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 422:
                    st.error(
                        f"Donnees invalides (422) : {exc.response.text}"
                    )
                else:
                    st.error(
                        f"Erreur API ({exc.response.status_code}) : {exc.response.text}"
                    )
                data = None
            except httpx.RequestError as exc:
                st.error(f"Erreur reseau inattendue : {exc!r}")
                data = None

        if data:
            st.success("Politique generee avec succes !")
            st.divider()
            policy_md = data.get("policy_markdown", "")
            if policy_md:
                st.markdown(policy_md)
            else:
                st.warning("La reponse ne contient pas de politique.")

            sources = data.get("sources", [])
            if sources:
                with st.expander(
                    f"Sources ({len(sources)})", expanded=False
                ):
                    for src in sources:
                        st.markdown(f"**{src.get('title', 'N/A')}**")
                        st.caption(src.get("content", ""))
                        st.divider()
