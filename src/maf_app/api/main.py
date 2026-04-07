"""FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from maf_app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="GOVAIAPP-MAF",
    description="AI Governance Policy Generator  MAF Edition",
    version="0.1.0",
)

app.include_router(router)
