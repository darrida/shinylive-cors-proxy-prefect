from crypt import methods

import httpx
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

client = httpx.AsyncClient()#base_url="https://api.prefect.cloud/api/")
base_url="https://api.prefect.cloud/api"

async def _reverse_proxy(request: Request):
    print("HERE", request.url.path.replace("/prefect-proxy/", ""))
    print(f"{base_url}/{request.url.path.replace("/prefect-proxy/", "")}")
    url = httpx.URL(path=f"{base_url}/{request.url.path.replace("/prefect-proxy/", "")}",
                    query=request.url.query.encode("utf-8"))
    print(url)
    rp_req = client.build_request(request.method, request.url.path.replace("/prefect-proxy/", ""), #url,
                                  headers=request.headers.raw,
                                  content=request.stream())
    rp_resp = await client.send(rp_req, stream=True)
    print(rp_resp)
    rp_resp.headers['Access-Control-Allow-Origin'] = '*'
    rp_resp.headers['Access-Control-Allow-Headers'] = '*'
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


async def homepage(request):
    return JSONResponse({'hello': 'world'})

app = Starlette(debug=True, routes=[
    Route('/', homepage),
])

from starlette.responses import Response


# @app.get("/prefect-proxy/{path:path}", methods=["GET", "POST"])
async def tile_request(path: str):
    async with httpx.AsyncClient() as client:
        proxy = await client.get(f"https://api.prefect.cloud/api/{path}")
    response = Response()
    response.body = proxy.content
    response.status_code = proxy.status_code
    return response

app.add_route("/prefect-proxy/{path:path}", tile_request, ["GET", "POST"])