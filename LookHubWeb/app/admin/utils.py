import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse, HTMLResponse


ADMIN_PREFIX = "/admin/flower"                   # куда монтируем в API

def _filter_headers(headers: dict) -> dict:
    excluded = {
        "content-encoding", "content-length", "transfer-encoding",
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "upgrade"
    }
    return {k: v for k, v in headers.items() if k.lower() not in excluded}


def _rewrite_flower_html(html: str) -> str:
    # переписываем ссылки в href/src
    html = html.replace('href="/flower', f'href="{ADMIN_PREFIX}')
    html = html.replace('src="/flower', f'src="{ADMIN_PREFIX}')
    html = html.replace('url: "/api/', f'url: "{ADMIN_PREFIX}/api/')
    html = html.replace('"/api/', f'"{ADMIN_PREFIX}/api/')
    html = html.replace("'/api/", f"'{ADMIN_PREFIX}/api/")
    return html


async def _proxy_request(request: Request, target: str) -> Response:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.request(
            method=request.method,
            url=target,
            content=await request.body(),
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            params=dict(request.query_params),
            timeout=None,
        )

        headers = _filter_headers(dict(resp.headers))
        content_type = resp.headers.get("content-type", "")

        if content_type.startswith("application/json"):
            return JSONResponse(content=resp.json(), status_code=resp.status_code, headers=headers)

        elif content_type.startswith("text/html"):
            body = (await resp.aread()).decode(resp.encoding or "utf-8")
            body = _rewrite_flower_html(body)

            # Встраиваем Flower в шаблон админки
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Админка - Flower</title>
                <!-- тут можно вставить свои стили/шапку админки -->
            </head>
            <body>
                <nav>
                    <!-- меню админки -->
                    <a href="/admin">Главная</a> |
                    <a href="{ADMIN_PREFIX}">Flower</a>
                </nav>
                <main>
                    {body}
                </main>
            </body>
            </html>
            """
            return HTMLResponse(content=html, status_code=resp.status_code, headers=headers)

        else:
            body = await resp.aread()
            return Response(content=body, status_code=resp.status_code, headers=headers)
