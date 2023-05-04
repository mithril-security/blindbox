from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/enclave')
async def get_enclave(request):
    return web.Response(text="[GET] /enclave : Server response")

@routes.post('/enclave/predict')
async def post_predict(request):
    data = await request.post()
    print("Receiving:", data['audio'])
    return web.Response(text="[GET] /enclave/predict : Server response")

app = web.Application()
app.add_routes(routes)
web.run_app(app)
