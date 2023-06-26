from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/enclave')
async def get_enclave(request):
    text = "[GET] /enclave : Server response"
    print(text)
    return web.Response(text=text)

@routes.options('/enclave')
async def options_enclave(request):
    text = "[OPTIONS] /enclave : Server response"
    print(text)
    return web.Response(text=text)

@routes.head('/enclave/head')
async def head_enclave(request):
    text = "[HEAD] /enclave/head : Server response"
    print(text)
    return web.Response(headers={"text" : text})

@routes.post('/enclave/predict')
async def post_predict(request):
    data = await request.post()
    text = "[POST] /enclave/predict : Server response"
    print(text, ": receiving:", data['audio'].filename)
    return web.Response(text=text)

@routes.put('/enclave')
async def put_enclave(request):
    data = await request.post()
    text = "[PUT] /enclave : Server response"
    print(text)
    return web.Response(text=text)

@routes.patch('/enclave')
async def patch_enclave(request):
    data = await request.post()
    text = "[PATCH] /enclave : Server response"
    print(text)
    return web.Response(text=text)

@routes.delete('/enclave')
async def delete_enclave(request):
    text = "[DELETE] /enclave : Server response"
    print(text)
    return web.Response(text=text)

app = web.Application()
app.add_routes(routes)
web.run_app(app, host='localhost', port=8080)
