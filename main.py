# from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.base import BaseHTTPMiddleware
# import jwt
# from jwt import InvalidTokenError
# from fastapi import HTTPException
# from pydantic import BaseModel

# import time
# import uuid

# app = FastAPI()

# ALLOWED_ORIGIN = "https://dash-hnl75k.example.com"

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[ALLOWED_ORIGIN],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class TimingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         start = time.perf_counter()

#         response = await call_next(request)

#         end = time.perf_counter()

#         response.headers["X-Request-ID"] = str(uuid.uuid4())
#         response.headers["X-Process-Time"] = f"{end-start:.6f}"

#         return response

# app.add_middleware(TimingMiddleware)

# @app.get("/stats")
# def stats(values: str = Query(...)):
#     nums = [int(x) for x in values.split(",")]

#     return {
#         "email": "24ds3000067@ds.study.iitm.ac.in",
#         "count": len(nums),
#         "sum": sum(nums),
#         "min": min(nums),
#         "max": max(nums),
#         "mean": sum(nums)/len(nums)
#     }
# PUBLIC_KEY = """
# -----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
# cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
# EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
# WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
# ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
# SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
# dQIDAQAB
# -----END PUBLIC KEY-----
# """

# ISSUER = "https://idp.exam.local"
# AUDIENCE = "tds-zqb4irrn.apps.exam.local"

# class TokenRequest(BaseModel):
#     token: str

#     @app.post("/verify")
# def verify(req: TokenRequest):

#     try:

#         payload = jwt.decode(
#             req.token,
#             PUBLIC_KEY,
#             algorithms=["RS256"],
#             audience=AUDIENCE,
#             issuer=ISSUER,
#         )

#         return {
#             "valid": True,
#             "email": payload.get("email"),
#             "sub": payload.get("sub"),
#             "aud": payload.get("aud"),
#         }

#     except InvalidTokenError:
#         raise HTTPException(
#             status_code=401,
#             detail={"valid": False},
#         )\

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from jwt import InvalidTokenError

import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-hnl75k.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        end = time.perf_counter()

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{end-start:.6f}"

        return response


app.add_middleware(TimingMiddleware)


@app.get("/stats")
def stats(values: str = Query(...)):
    nums = [int(x) for x in values.split(",")]

    return {
        "email": "24ds3000067@ds.study.iitm.ac.in",
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }


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