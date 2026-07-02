from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
import jwt
from jwt import InvalidTokenError
import time
import uuid
import os
import yaml
from dotenv import load_dotenv

# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-hnl75k.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Middleware
# ---------------------------------------------------

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{time.perf_counter()-start:.6f}"

        return response


app.add_middleware(TimingMiddleware)

# ---------------------------------------------------
# Assignment 1 : Stats
# ---------------------------------------------------

EMAIL = "24ds3000067@ds.study.iitm.ac.in"


@app.get("/stats")
def stats(values: str = Query(...)):
    nums = [int(x) for x in values.split(",")]

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }


# ---------------------------------------------------
# Assignment 2 : JWT Verify
# ---------------------------------------------------

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-zqb4irrn.apps.exam.local"


class TokenRequest(BaseModel):
    token: str


@app.post("/verify")
def verify(req: TokenRequest):
    try:
        payload = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={"valid": False},
        )


# ---------------------------------------------------
# Assignment 3 : Effective Config
# ---------------------------------------------------

load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(request: Request):

    config = DEFAULTS.copy()

    # YAML layer
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            yaml_data = yaml.safe_load(f)
            if yaml_data:
                config.update(yaml_data)

    # .env layer
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_DEBUG"):
        config["debug"] = to_bool(os.getenv("APP_DEBUG"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # OS Environment (APP_*)
    if "APP_DEBUG" in os.environ:
        config["debug"] = to_bool(os.environ["APP_DEBUG"])

    # CLI Overrides
    for item in request.query_params.getlist("set"):

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "port":
            config["port"] = int(value)

        elif key == "workers":
            config["workers"] = int(value)

        elif key == "debug":
            config["debug"] = to_bool(value)

        else:
            config[key] = value

    # Never expose API key
    config["api_key"] = "****"

    return config