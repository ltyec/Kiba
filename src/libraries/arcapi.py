import aiohttp, websockets, json, brotli

url = 'https://webapi.lowiro.com/'
me = 'webapi/user/me'
login = 'auth/login'
est = 'wss://arc.estertion.win:616/'

async def get_web_api(email, password):
    data = {'email': email, 'password': password}
    async with aiohttp.ClientSession() as session:
        async with session.post(url + login, data=data) as req:
            if req.status != 200:
                return '▿ Kiba - ArcAPI\n查询用账号异常，请联系 Kiba 超级管理员'
        async with session.get(url + me) as reqs:
            return await reqs.json()

async def arcb30(arcid: str, re: bool = False):
    try:
        b30_data = []
        async with websockets.connect(est, timeout=10) as ws:
            await ws.send(str(arcid))
            while True:
                if ws.closed:
                    break
                data = await ws.recv()
                if data == 'error,add':
                    return '▿ Kiba - ArcAPI\n连接查分器错误。'
                elif data == 'bye':
                    return b30_data
                elif isinstance(data, bytes):
                    info = json.loads(brotli.decompress(data))
                    if info['cmd'] == 'userinfo' and re:
                        return info
                    elif info['cmd'] == 'scores' or info['cmd'] == 'userinfo':
                        b30_data.append(info)
    except websockets.ConnectionClosedError as e:
        return '▿ Kiba - ArcAPI\n当前可能在排队，请您暂时停用 <arcinfo> 和 <arcre:> 指令。'
    except Exception as e:
        return f'▿ Kiba - ArcAPI\n查询失败。可能是网络数据库连接有问题，请检查是否正在版本更新？\n[Exception Occurred]\n{e}'
