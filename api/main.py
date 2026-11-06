from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.recommender import Recommender
from src.llm.anthropic_provider import AnthropicProvider
from src.explanations import GroundedExplanationGenerator
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="AI Recommender API",
    version="1.0.0",
    description=(
        "Adaptive e-commerce recommendation system using "
        "content-based retrieval, behavioral co-visitation, "
        "learned reranking, intent-aware ranking, and "
        "grounded recommendation explanations."
    ),

)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Frontend build location (React/Vite output)
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

# First path segments that belong to the API and must never
# fall through to the single-page-app fallback.
API_PATH_PREFIXES = {
    "recommend",
    "health",
    "docs",
    "redoc",
    "openapi.json",
}

INDEX_HEADERS = {"Cache-Control": "no-cache"}


def frontend_is_built() -> bool:
    return FRONTEND_INDEX.is_file()


# ============================================================
# Core services
# ============================================================

recommender = Recommender()

explanation_generator = GroundedExplanationGenerator()


# ============================================================
# Request schemas
# ============================================================

class IntelligentRecommendationRequest(BaseModel):
    user_id: int

    query: str = Field(
        min_length=1
    )

    k: int = Field(
        default=10,
        ge=1,
        le=100
    )


# ============================================================
# Helper
# ============================================================

def recommendations_to_records(
    recommendations
):
    """
    Convert recommendation output into a JSON-safe list.
    """

    # Newer structure:
    # {
    #     "segment": ...,
    #     "recommendations": DataFrame,
    #     ...
    # }

    if isinstance(
        recommendations,
        dict
    ):
        nested = recommendations.get(
            "recommendations",
            []
        )

        if hasattr(
            nested,
            "to_dict"
        ):
            return nested.to_dict(
                orient="records"
            )

        if isinstance(
            nested,
            list
        ):
            return nested

        return []

    # Original pandas DataFrame output

    if hasattr(
        recommendations,
        "to_dict"
    ):
        return recommendations.to_dict(
            orient="records"
        )

    # Already JSON-ready

    if isinstance(
        recommendations,
        list
    ):
        return recommendations

    raise TypeError(
        "Unsupported recommendation "
        f"output type: {type(recommendations)}"
    )


# ============================================================
# Basic routes
# ============================================================

@app.get("/", include_in_schema=False)
def root():
    # Serve the React app when it has been built;
    # otherwise keep the original API status message.
    if frontend_is_built():
        return FileResponse(
            FRONTEND_INDEX,
            headers=INDEX_HEADERS
        )

    return {
        "message":
            "AI Recommender API is running",
        "frontend":
            "Not built. Run `npm run build` "
            "inside frontend/ to serve the UI here."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# Standard recommendation endpoint
# ============================================================

@app.get(
    "/recommend/{user_id}"
)
def recommend(
    user_id: int,
    k: int = 10
):
    if k < 1 or k > 100:
        raise HTTPException(
            status_code=400,
            detail="k must be between 1 and 100"
        )

    try:
        result = recommender.recommend(
            user_id=user_id,
            k=k
        )

        segment = (
            recommender.router
            .get_segment(
                user_id
            )
        )

        records = recommendations_to_records(
            result
        )

        return {
            "user_id": user_id,
            "segment": segment,
            "count": len(records),
            "recommendations": records,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Recommendation generation "
                f"failed: {exc}"
            )
        ) from exc


# ============================================================
# Intelligent natural-language endpoint
# ============================================================

@app.post(
    "/recommend/intelligent"
)
def intelligent_recommendation(
    request: IntelligentRecommendationRequest
):
    # 1. Initialize Claude only when needed

    try:
        intent_provider = AnthropicProvider()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    # 2. Parse natural language into UserIntent

    try:
        intent = intent_provider.parse_intent(
            request.query
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Intent parsing failed: "
                f"{exc}"
            )
        ) from exc

    # 3. Run ML recommender with evidence

    try:
        result = (
            recommender
            .recommend_with_evidence(
                user_id=request.user_id,
                k=request.k,
                intent=intent
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Recommendation generation "
                f"failed: {exc}"
            )
        ) from exc

    # 4. Convert recommendations to JSON-safe records

    recommendations = (
        recommendations_to_records(
            result
        )
    )

    # 5. Evidence

    evidence = result.get(
        "evidence",
        []
    )

    # 6. Grounded explanations

    try:
        explanations = (
            explanation_generator
            .generate(
                evidence,
                intent=intent
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Explanation generation "
                f"failed: {exc}"
            )
        ) from exc

    # 7. Final response

    return {
        "user_id":
            request.user_id,

        "query":
            request.query,

        "segment":
            result.get(
                "segment",
                recommender.router
                .get_segment(
                    request.user_id
                )
            ),

        "parsed_intent":
            intent.to_dict(),

        "recommendations":
            recommendations,

        "evidence":
            evidence,

        "explanations":
            explanations,

        "unverifiable_constraints":
            (
                intent
                .unverifiable_constraints
                or []
            ),
    }


# ============================================================
# React frontend (single-server hosting)
#
# Registered LAST so every API route above matches first.
# ============================================================

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="frontend-assets",
    )


@app.get(
    "/{full_path:path}",
    include_in_schema=False
)
def serve_frontend(full_path: str):
    first_segment = full_path.split("/", 1)[0]

    # Unknown API-looking paths get a real 404,
    # never the HTML page.
    if first_segment in API_PATH_PREFIXES:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

    if not frontend_is_built():
        raise HTTPException(
            status_code=404,
            detail=(
                "Frontend not built. Run "
                "`npm run build` inside frontend/."
            )
        )

    # Top-level files from the build (favicon.svg etc.),
    # guarded against path traversal.
    dist_root = FRONTEND_DIST.resolve()
    candidate = (dist_root / full_path).resolve()

    if (
        full_path
        and candidate.is_file()
        and dist_root in candidate.parents
    ):
        return FileResponse(candidate)

    # Any other client-side route gets the SPA shell.
    return FileResponse(
        FRONTEND_INDEX,
        headers=INDEX_HEADERS
    )