"""
PROTEX Research Prototype
Query API (public research edition)

This module demonstrates controlled hybrid retrieval logic
without production configuration.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "system": "PROTEX Research Prototype",
        "status": "active",
        "description": "Controlled hybrid retrieval architecture for structured case analysis."
    }
