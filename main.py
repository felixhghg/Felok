import asyncio
import base64
import json
import os.path
import random
import string

import colorama
import uvicorn
from fastapi import FastAPI, Body
from starlette.responses import HTMLResponse, Response
from telethon import events
from telethon.tl.types import MessageEntityCode, MessageEntityPre

import loader
from FelokClient import FelokClient, FelokBot
from cipher import encrypt_data, decrypt_data

cl: FelokClient | None = None
app = FastAPI()

def openf(f):
    return open(f, 'r', encoding='utf-8').read()
@app.get("/")
async def index():
    return HTMLResponse(openf("./web/index.html"))

@app.get("/style.css")
async def style():
    return Response(openf("./web/style.css"))

@app.get("/assets/{f}")
async def assets(f):
    return Response(open(f"./web/assets/{f}","rb").read())

@app.post("/")
async def p(data = Body()):
    global cl
    cl = FelokClient(api_id=data["api_id"],api_hash=data["api_hash"],phone=data["phone"])
    uba = await cl.start_ub()
    return Response(uba)

@app.post("/c")
async def c(data = Body()):
    global cl
    uba = await cl.sign_ub(data["code"])
    if uba == "done":
        save_creds(cl._api_id, cl._api_hash, cl.phone)
        asyncio.create_task(start_Felok(fr=True))
    return Response(uba)

@app.post("/p")
async def p(data = Body()):
    global cl
    uba = await cl.resign_ub(data["password"])
    if uba == "done":
        save_creds(cl._api_id,cl._api_hash,cl.phone)
        asyncio.create_task(start_Felok(fr=True))
    return Response(uba)

def save_creds(api_id, api_hash, phone, bot_token=None):
    cred = {"ai": api_id, "ah": api_hash, "pn": phone}
    if bot_token: cred["bt"] = bot_token
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cfg.json"), "wb") as f:
        f.write(base64.b64encode(encrypt_data(json.dumps(cred))))


def add_creds(bot_token):
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cfg.json")
    with open(cfg_path, "rb") as f:
        tosave = json.loads(decrypt_data(base64.b64decode(f.read())))
    tosave["bt"] = bot_token
    with open(cfg_path, "wb") as f:
        f.write(base64.b64encode(encrypt_data(json.dumps(tosave))))


def check_Felok():
    files = ["Felok.key","Felok.session","cfg.json"]
    for i in files:
        if not os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), i)):
            return False
    return True


def load_FelokClient():
    global cl
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cfg.json")
    if cl is None:
        with open(cfg_path, "rb") as f:
            cfg = json.loads(decrypt_data(base64.b64decode(f.read())))
        cl = FelokClient(api_id=cfg["ai"], api_hash=cfg["ah"], phone=cfg["pn"])

        if "bt" in cfg:
            cl._bsession = FelokBot(api_id=cfg["ai"], api_hash=cfg["ah"], bot_token=cfg["bt"])
    elif cl._bsession is None:
        with open(cfg_path, "rb") as f:
            cfg = json.loads(decrypt_data(base64.b64decode(f.read())))

        if "bt" in cfg:
            cl._bsession = FelokBot(api_id=cfg["ai"], api_hash=cfg["ah"], bot_token=cfg["bt"])

def create_Felok_US():
    L = list(string.ascii_lowercase + string.digits)
    FS = "Felok_"
    for i in range(5):
        FS += random.choice(L)
    return FS+"_bot"

def ET(msg):
    text = msg.raw_text
    if not msg.entities:
        return None
    for e in msg.entities:
        if isinstance(e, (MessageEntityCode, MessageEntityPre)):
            return text[e.offset : e.offset + e.length]
    return None

async def sbf(ms):
    async with cl.conversation(93372553) as conv:
        await conv.send_message(ms)
        response = await conv.get_response()

        await cl.delete_messages(93372553, [response.id, response.id - 1])

        return response


def reduce(strx, num):
    final = strx
    if len(strx) > num:
        final = strx[:num]
        final += "..."

    return final


async def start_Felok(fr = False):
    global cl
    if not check_Felok(): return "FilesMissing"
    load_FelokClient()

    await cl.connect()

    if fr:
        USR = await cl.get_me()
        FU = create_Felok_US()
        await cl.get_input_entity('@BotFather')


        await sbf("/start")
        await asyncio.sleep(random.randint(1,2))

        await sbf("/newbot")
        await asyncio.sleep(random.randint(1,2))

        await sbf(f"Felok⛏ {reduce(USR.username,5)}")

        await sbf(FU)
        await asyncio.sleep(random.randint(1,2))


        await sbf("/token")
        await asyncio.sleep(random.randint(1,2))

        m = await sbf(f"@{FU}")
        tok = ET(m).strip()

        add_creds(tok)

        await asyncio.sleep(random.randint(1,2))

        await sbf("/setinline")
        await asyncio.sleep(random.randint(1,2))

        await sbf(f"@{FU}")
        await asyncio.sleep(random.randint(1,2))

        await sbf(f"Felok: {USR.username}")
        await asyncio.sleep(random.randint(1,2))

        await sbf("/setinlinefeedback")
        await asyncio.sleep(random.randint(1,2))

        await sbf(f"@{FU}")
        await asyncio.sleep(random.randint(1,2))

        await sbf(f"Enabled")
        await asyncio.sleep(random.randint(1, 2))


        await cl.get_input_entity(f'@{FU}')

        load_FelokClient()
        if cl._bsession:
            await asyncio.sleep(10)
            await cl._bsession.start_bot()



        s = await cl.send_message(f"@{FU}","/start")
        await cl.delete_messages(f"@{FU}",s.id)
        await cl._bsession.send_message(USR.id,"Привет! Ты установил Felok Userbot, на данный момент этот юзербот находится в разработке\n\nРазработку ведёт команда: @Cubefel")

    loader.cl = cl
    loader.load_modules()



    tasks = [cl.run_until_disconnected()]
    if cl._bsession:
        await cl._bsession.connect()
        if not cl._bsession.is_connected():
            await cl._bsession.start_bot()
        tasks.append(cl._bsession.run_until_disconnected())

    await asyncio.gather(*tasks)


if __name__ == "__main__":

    print(colorama.Fore.LIGHTCYAN_EX + r"""
 ________         __            __             
/        |       /  |          /  |            
$$$$$$$$/______  $$ |  ______  $$ |   __       
$$ |__  /      \ $$ | /      \ $$ |  /  |      
$$    |/$$$$$$  |$$ |/$$$$$$  |$$ |_/$$/       
$$$$$/ $$    $$ |$$ |$$ |  $$ |$$   $$<        
$$ |   $$$$$$$$/ $$ |$$ \__$$ |$$$$$$  \       
$$ |   $$       |$$ |$$    $$/ $$ | $$  |      
$$/     $$$$$$$/ $$/  $$$$$$/  $$/   $$/       
                                               
                                                                               
    """ + colorama.Fore.LIGHTWHITE_EX + """Felok Userbot 1.0\n\nby: @cubefel""")

    if check_Felok():
        asyncio.run(start_Felok(fr=False))
    else:
        site_port = random.randint(1,65535)
        print(f"""Вам необходимо перейти по ссылке http://127.0.0.1:{site_port} """)
        uvicorn.run(app, host="0.0.0.0", port=site_port,access_log=False,log_level="error")
