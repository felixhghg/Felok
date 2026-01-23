import asyncio
import hashlib
import time
from typing import Optional, Callable, Any
from telethon import Button, events

from FelokClient import FelokClient


cl: Optional[FelokClient] = None
funcs: Optional[dict[str,Callable[..., Any]]] = {}

class InlineButton():
    def __init__(
            self,
            text: str,
            callback: Optional[str] = None,
            url: Optional[str] = None,
            callfunc: Optional[Callable[..., Any]] = None
    ):
        """
        InlineButton Класс кнопки, нужно выбрать один опциональный
        :param text: Обязателен, текст кнопки
        :param callback: Опционально, коллбек обрабатывай с помощью loader
        :param url: Опционально, ссылка
        :param callfunc: Опционально, функция которая вызывется вместо callback
        """
        global funcs
        if not text:
            raise "Text is not specified"

        act = [bool(callback), bool(url), bool(callfunc)]
        active_acts = sum(act)

        if active_acts == 0:
            raise ValueError("You must specify at least one action: callback, url, or callfunc")

        if active_acts > 1:
            raise ValueError("Too many actions specified. Choose only one: callback, url, or callfunc")

        self.text = text
        self.callback = callback
        self.url = url
        self.callfunc = callfunc

        if url:
            self.button = Button.url(text, url)
        elif callback:
            self.callback = callback.encode() if isinstance(callback, str) else callback
            if len(self.callback) > 64:
                raise ValueError("Callback data exceeds 64 bytes")
            self.button = Button.inline(text, self.callback)
        elif callfunc:

            seed = f"{id(callfunc)}{time.time()}".encode()
            hash_str = hashlib.md5(seed).hexdigest()[:12]
            funcs[hash_str] = callfunc
            self.callback = hash_str
            self.button = Button.inline(text, self.callback)

def build_rows(btns):
    if isinstance(btns, list):
       return [build_rows(b) for b in btns]
    return btns.button if hasattr(btns, 'button') else btns

async def send_buttons(entity: Any,
                       text: str,
                       buttons: list | Any,
                       file: Optional[Any] = None,
                       **kwargs):
    """
        Отправка сообщений с кнопками(или без)
        :param entity: (ID, username или объект диалога)
        :param text: Текст сообщения
        :param buttons: Список [InlineButton] или список списков [[InlineButton]]
        :param file: Если передано, отправит как медиа (фото/документ)
    """

    buttons_to_send = build_rows(buttons)



    temp_phr = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]



    async def tmp(event: events.InlineQuery.Event):
        if event.text != temp_phr: return
        builder = event.builder
        results = []

        if file:

            results.append(
                builder.photo(
                    file,
                    text=text,
                    buttons=buttons_to_send
                )
            )
        else:

            results.append(
                builder.article(
                    title="0",
                    text=text,
                    description="i'm nut",
                    buttons=buttons_to_send
                )
            )

        await event.answer(results)

        cl._bsession.remove_event_handler(tmp, events.InlineQuery)

    cl._bsession.add_event_handler(tmp, events.InlineQuery)
    bot = await cl._bsession.get_me()
    results = await asyncio.wait_for(cl.inline_query(bot.username, temp_phr), timeout=10.0)
    if results:
        return await results[0].click(entity, **kwargs)
    cl._bsession.remove_event_handler(tmp, events.InlineQuery)
    return None


async def setup_callfuncs():
    if cl._bsession:
        @cl._bsession.on(events.CallbackQuery)
        async def handle_funcs(event):
            data = event.data.decode("utf-8")
            if data in funcs:
                try:
                    data = event.data.decode("utf-8")
                    if data in funcs:
                        func = funcs[data]
                        await func(event)
                except Exception as e:
                    print(f"Error in Inline CallFunc: {e}")