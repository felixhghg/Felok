import importlib.util
import os.path
import sys
from functools import wraps
import inspect

import telethon.events.newmessage
from telethon import events

from FelokClient import FelokClient

mp = os.path.join(os.path.dirname(os.path.abspath(__file__)),"modules")
cl: FelokClient | None = None
builtinx = ["mloader","loader"]
loaded_modules = {}

ENM = telethon.events.NewMessage.Event

def command(cmd="", outgoing=True, incoming=False):
    """Декоратор для обработки комманд
    :param cmd: Команда
    :param outgoing: Фильтр исходящие сообщения
    :param incoming: Фильтр приходящие сообщения
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = args[-1]
            if event.raw_text and cl and event.raw_text.startswith(cl.prefix + cmd):
                return await func(*args, **kwargs)
            return None

        wrapper._is_command = True
        wrapper._config = {'outgoing': outgoing, 'incoming': incoming}

        return wrapper
    return decorator


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
                    for m_name, method in inspect.getmembers(instance, inspect.iscoroutinefunction):
                        if hasattr(method, "_is_command") and cl:
                            conf = method._config
                            cl.add_event_handler(method, events.NewMessage(**conf))
                            loaded_modules[mn].append(method)
            return True, meta
        except Exception as e:
            print(f"ERR loading {mn}: {e}")
            return False, None
    return False, None


def remove_module(mn: str):
    if mn in loaded_modules and mn.lower() not in builtinx:
        for h in loaded_modules[mn]:
            cl.remove_event_handler(h)
        del loaded_modules[mn]


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
    for f in os.listdir(mp):
        if f.endswith(".py") and f != "__init__.py":
            install_module(os.path.join(mp, f),True)
