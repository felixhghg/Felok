import datetime
import importlib.util
import os.path
import re
import sys
from functools import wraps
import inspect
from linecache import cache

import telethon.events.newmessage
from telethon import events
from telethon.events import InlineQuery
from telethon.tl.types import MessageEntityCustomEmoji
from utils import html_deparse,html_parse
from FelokClient import FelokClient
from database import Database

mp = os.path.join(os.path.dirname(os.path.abspath(__file__)),"modules")
cl: FelokClient | None = None
builtinx = ["mloader","loader","security"]
loaded_modules = {}
inline_queries = {}
module_commands = {}
inline_answers = []

ENM = telethon.events.NewMessage.Event
ECQ = telethon.events.CallbackQuery.Event
EIQ = telethon.events.InlineQuery.Event

start_time = datetime.datetime.now()

def uptime():
    return datetime.datetime.now()-start_time

def iscmd(raw_text, param):
    return raw_text == param or raw_text.startswith(param+" ")




def command(cmd="", outgoing=True, incoming=False, rank:int=None, aliases=list()):
    """Декоратор для обработки комманд
    :param cmd: Команда
    :param outgoing: Фильтр исходящие сообщения
    :param incoming: Фильтр приходящие сообщения
    :param rank: ранг пользователя
    :param aliases: Псевдонимы
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = args[-1]

            if not event.sender:
                await event.get_sender()


            if event.raw_text and cl:
                possible_commands = [cmd] + aliases
                for c in possible_commands:
                    if iscmd(event.raw_text,cl.prefix+c):
                        if hasattr(args[0], 'db') and rank:
                            if not args[0].db.check_access(event, rank):
                                return None

                        event.raw_text = html_deparse(event.message.raw_text,event.message.entities)
                        event.message.raw_text = event.raw_text


                        return await func(*args, **kwargs)
            return None

        wrapper._is_command = True
        wrapper._cmd = [cmd] + aliases
        wrapper._config = {'outgoing': outgoing, 'incoming': True if rank is not None else incoming}
        wrapper._rank = rank
        return wrapper
    return decorator

def watcher(outgoing=True, incoming=False, rank:int=None, sticker=True, gif=True, video_note=True, voice=True, video=True, photo=True, document=True):
    """Декоратор для обработки ВСЕХ новых сообщений
    :param outgoing: Фильтр исходящие сообщения
    :param incoming: Фильтр приходящие сообщения
    :param rank: ранг пользователя
    :param sticker: обрабатывать стикеры?
    :param gif: обрабатывать гифки?
    :param video_note: обрабатывать кружки?
    :param voice: обрабатывать голос?
    :param video: обрабатывать видео?
    :param photo: обрабатывать фото?
    :param document: обрабатывать файлы? Все сообщения которые не текстовые
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            event: ENM = args[-1]

            if not event.sender:
                await event.get_sender()

            if hasattr(args[0], 'db') and rank:
                if not args[0].db.check_access(event,rank):
                    return None


            if event.message.sticker and not sticker or event.message.gif and not gif or event.message.video_note and not video_note or event.message.voice and not voice or event.message.video and not video or event.message.photo and not photo or event.message.document and not document:
                return None

            event.raw_text = html_deparse(event.message.raw_text, event.message.entities)
            event.message.raw_text = event.raw_text
            return await func(*args, **kwargs)

        wrapper._is_watcher = True
        wrapper._config = {'outgoing': outgoing, 'incoming': True if rank is not None else incoming}
        wrapper._rank = rank

        return wrapper
    return decorator

def query(rank:int = None):
    """
    обрабатывать InlineQuery
    ответ отправлять return-ом
    :param rank: ранг пользователя
    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args,**kwargs):
            event: EIQ = args[-1]
            if hasattr(args[0], 'db') and rank:
                if not args[0].db.check_access(event,rank):
                    return None
            retu = await func(*args, **kwargs)
            if type(retu) == list:
                inline_answers.extend(retu)
            return retu

        wrapper._is_query = True
        wrapper._config = {}
        wrapper._rank = rank
        return wrapper
    return decorator

async def _ans_query(event: EIQ):
    global inline_answers
    await event.fanswer(inline_answers,cache_time=0)
    inline_answers = []




def install_module(file_path,force=False):
    if not file_path.endswith(".py"):
        return False, None

    mn = os.path.basename(file_path)[:-3]
    if mn.lower() in builtinx and not force: return (False,"builtin")
    if mn in loaded_modules: return (False,"already")
    loaded_modules[mn] = []
    spec = importlib.util.spec_from_file_location(mn, file_path)

    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        sys.modules[mn] = m
        try:
            spec.loader.exec_module(m)
            meta = {}
            for name, obj in inspect.getmembers(m):
                if inspect.isclass(obj) and obj.__module__ == m.__name__:
                    instance = obj()
                    meta = {
                        "name": getattr(instance, "name", mn),
                        "description": getattr(instance, "description", "Нет описания"),
                        "version": getattr(instance, "version", "1.0")
                    }
                    instance.db = Database(owner=mn)
                    module_commands[mn] = []
                    inline_queries[mn] = []
                    try:
                        cl._bsession.remove_event_handler(_ans_query)
                    except:
                        pass
                    for m_name, method in inspect.getmembers(instance, inspect.iscoroutinefunction):

                        if hasattr(method, "_is_command") and cl:
                            conf = method._config
                            cl.add_event_handler(method, events.NewMessage(**conf))
                            loaded_modules[mn].append(method)
                            module_commands[mn].append(method._cmd)
                        if hasattr(method, "_is_watcher") and cl:
                            conf = method._config
                            cl.add_event_handler(method, events.NewMessage(**conf))
                            loaded_modules[mn].append(method)
                        if hasattr(method, "_is_query"):
                            cl._bsession.add_event_handler(method, events.InlineQuery())
                            inline_queries[mn].append(method)
                            loaded_modules[mn].append(method)
                    cl._bsession.add_event_handler(_ans_query, events.InlineQuery())
            return True, meta
        except Exception as e:
            print(f"ERR loading {mn}: {e}")
            return False, None
    return False, None


def remove_module(mn1: str):
    mn = mn1.lower()
    if mn in loaded_modules and mn.lower() not in builtinx:
        for h in loaded_modules[mn]:
            cl.remove_event_handler(h)
        del loaded_modules[mn]
        del module_commands[mn]
        del inline_queries[mn]

        db = Database(owner=mn)
        db.clear()

        if mn in sys.modules:
            del sys.modules[mn]

        fp = os.path.join(mp,f"{mn}.py")
        if os.path.exists(fp):
            os.remove(fp)
            return True
    elif mn.lower() in builtinx:
        return "builtin"
    return False

def load_modules():
    if not os.path.exists(mp):
        os.makedirs(mp)
        return
    ls = os.listdir(mp)
    ls.remove("__pycache__")
    fls = [l for l in ls]
    for x in ls:
        if x.endswith(".py") and x.lower()[::-1].split(".",maxsplit=1)[::-1][0][::-1] in builtinx:
            install_module(os.path.join(mp, x), True)
            fls.remove(x)
    for f in fls:
        if f.endswith(".py") and f != "__init__.py":
            install_module(os.path.join(mp, f),True)
