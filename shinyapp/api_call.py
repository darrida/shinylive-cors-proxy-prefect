import json

# from lib2to3.pytree import Base
from typing import Any, Literal

from pydantic import BaseModel
from shiny import ui


class HttpResponse(BaseModel):
    status: str|int
    data: bytes|dict|str


class PyFetch(BaseModel):
    type: str
    status: int|str
    # headers: dict = None
    redirected: bool
    ok: bool
    data: dict|str|int|bytes = None
    response: Any = None

    def __str__(self):
        return f"{self.status}, {self.redirected}, {self.ok}, {self.data}, {self.type}, {self.response}"

    @staticmethod
    async def call(url: str, headers: dict = None, method: str = None, clone: bool = False, **kwargs) -> "PyFetch":
        import js
        import pyodide

        r = await pyodide.http.pyfetch(url=url, headers=headers, method="GET", **kwargs)

        response = r.clone() if clone is True else r

        fetch = PyFetch(
            response = response,
            status = r.status,
            type = r.type,
            ok = r.ok,
            redirected = r.redirected
        )
        ui.notification_show(str(fetch), duration=100)
        if fetch.type in ("json", "cors"):
            fetch.data = await fetch.json()
        elif fetch.type == "string":
            fetch.data = await fetch.string()
        elif fetch.type == "bytes":
            fetch.data = await fetch.bytes()
        else:
            fetch.data = f"Response type not accounted for: {fetch.type}"
        return fetch

    async def json(self):
        return await self.response.json()

    async def string(self):
        return await self.response.string()

    async def buffer(self):
        return await self.response.bufFer()
    
    async def bytes(self):
        return await self.response.bytes()
    
    def raise_for_status(self):
        return self.response.raise_for_status()

    


async def get_url(
    url: str, headers: dict = None, clone: bool = False, type: Literal["string", "bytes", "json"] = "string", **kwargs
) -> HttpResponse:
    """
    An async wrapper function for http requests that works in both regular Python and
    Pyodide.

    In Pyodide, it uses the pyodide.http.pyfetch() function, which is a wrapper for the
    JavaScript fetch() function. pyfetch() is asynchronous, so this whole function must
    also be async.

    In regular Python, it uses the urllib.request.urlopen() function.

    Args:
        url: The URL to download.

        type: How to parse the content. If "string", it returns the response as a
        string. If "bytes", it returns the response as a bytes object. If "json", it
        parses the reponse as JSON, then converts it to a Python object, usually a
        dictionary or list.

    Returns:
        A HttpResponse object
    """
    import sys

    if "pyodide" in sys.modules:
        response = await PyFetch.call(url=url, headers=headers, clone=clone, **kwargs)
        return HttpResponse(status=response.status, data=response.data)
    else:
        from urllib.request import Request, urlopen

        request = Request(url, headers=headers)
        if headers is not None:
            for header, value in headers.items():
                request.add_header(header, value)
        response = urlopen(request)
        if type == "json":
            data = json.loads(response.read().decode("utf-8"))
        elif type == "string":
            data = response.read().decode("utf-8")
        elif type == "bytes":
            data = response.read()
        elif type == "csv":
            with open("test.csv", "wb") as f:
                f.write(response.read())
            data = "test.csv"

        return HttpResponse(status=response.status, data=data)
