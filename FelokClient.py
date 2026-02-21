import asyncio
import hashlib

from telethon import TelegramClient, functions, events, types
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError, \
    PhoneCodeInvalidError
from telethon.tl.custom import InlineBuilder

import loader
from utils import html_deparse,html_parse

def get_p():
    with open("./p","r") as f:
        return f.readlines()[0]

class FelokClient(TelegramClient):
    BLACK_LIST_REQUESTS = (
        functions.account.DeleteAccountRequest,
        functions.account.UpdatePasswordSettingsRequest,
        functions.auth.LogOutRequest
    )

    def __init__(self,api_id,api_hash,phone,session = "Felok"):

        self._api_id = api_id
        self._api_hash = api_hash
        self.phone = phone
        self._session: str | None = session
        self._bsession: FelokBot | None = None
        self.prefix = get_p()

        super().__init__(session, api_id, api_hash, device_model="F 64bit", system_version="F1", app_version="5.1.7", lang_code="ru", system_lang_code="ru")



    async def __call__(self, request, ordered= False,flood_sleep_threshold=None):
        if isinstance(request,self.BLACK_LIST_REQUESTS):
            raise PermissionError("BLACKLISTED REQUESTS")

        return await super().__call__(request,ordered,flood_sleep_threshold)

    async def send_message(self, entity, message=None, *args, **kwargs):
        target = message
        if target and kwargs.get("parse_mode") == "html":
            clean_text, entities = html_parse(target)
            kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + entities

            target = clean_text
        return await super().send_message(entity, target, *args, **kwargs)

    async def edit_message(self, entity, message=None, text=None, *args, **kwargs):
        target = text
        if target and kwargs.get("parse_mode") == "html":
            clean_text, entities = html_parse(target)
            kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + entities

            target = clean_text
        try:
            await super().edit_message(entity, message,target, *args, **kwargs)
        except:
            await super().send_message(entity,target,*args,**kwargs)
        return

    async def send_file(self, entity, file, caption=None, *args, **kwargs):
        target = caption
        if target and kwargs.get("parse_mode") == "html":
            all_entities = []

            if isinstance(target, str):
                clean_text, entities = html_parse(target)
                target = clean_text
                all_entities = entities
            elif isinstance(target, list):
                processed_captions = []
                for cap_item in target:
                    if isinstance(cap_item, str):
                        clean_text, entities = html_parse(cap_item)
                        processed_captions.append(clean_text)
                        all_entities.extend(entities)
                    else:
                        processed_captions.append(cap_item)
                target = processed_captions

            if all_entities:
                kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + all_entities


        return await super().send_file(entity, file, caption=target, *args, **kwargs)

    async def start_ub(self):
        await self.connect()

        if not await self.is_user_authorized():
            try:
                await self.send_code_request(str(self.phone))
                return "code"
            except:
                return "nope"


    async def sign_ub(self,code):
        try:
            await self.sign_in(self.phone,code)
            return "done"
        except PhoneCodeInvalidError:
            return "incorrect"
        except SessionPasswordNeededError:
            return "password"

    async def resign_ub(self,psw):
        try:
            await self.sign_in(password=psw)
            return "done"
        except PasswordHashInvalidError:
            return "password"


class FelokBot(TelegramClient):
    BLACK_LIST_REQUESTS = (
        functions.account.DeleteAccountRequest,
        functions.account.UpdatePasswordSettingsRequest,
        functions.auth.LogOutRequest
    )

    def __init__(self,api_id,api_hash,bot_token,session="BFelok"):
        self._bot_token = bot_token
        super().__init__(session,api_id,api_hash,device_model="FB 64bit",system_version="FB1",app_version="5.1.7",lang_code="ru",system_lang_code="ru")
        self._patch()

    def _patch(self):

        async def answer(
                self, results=None, cache_time=0, *,
                gallery=False, next_offset=None, private=False,
                switch_pm=None, switch_pm_param=''):


            if self._answered:
                return []

            loader.extres(results)

            return (results,True)

        events.InlineQuery.Event.answer = answer


        async def full_answer(self, results=None, cache_time=0, *,
                gallery=False, next_offset=None, private=False,
                switch_pm=None, switch_pm_param=''):


            if self._answered:
                return []

            if results:
                futures = [self._as_future(x) for x in results]

                await asyncio.wait(futures)

                results = [x.result() for x in futures]
            else:
                results = []

            if switch_pm:
                switch_pm = types.InlineBotSwitchPM(switch_pm, switch_pm_param)

            return await self._client(
                functions.messages.SetInlineBotResultsRequest(
                    query_id=self.query.query_id,
                    results=results,
                    cache_time=cache_time,
                    gallery=gallery,
                    next_offset=next_offset,
                    private=private,
                    switch_pm=switch_pm
                )
            )

        events.InlineQuery.Event.fanswer = full_answer

        async def article(
                self, title, description=None,
                *, url=None, thumb=None, content=None,
                id=None, text=None, parse_mode=(), link_preview=True,
                geo=None, period=60, contact=None, game=False, buttons=None
        ):
            """
            Creates new inline result of article type.

            Args:
                title (`str`):
                    The title to be shown for this result.

                description (`str`, optional):
                    Further explanation of what this result means.

                url (`str`, optional):
                    The URL to be shown for this result.

                thumb (:tl:`InputWebDocument`, optional):
                    The thumbnail to be shown for this result.
                    For now it has to be a :tl:`InputWebDocument` if present.

                content (:tl:`InputWebDocument`, optional):
                    The content to be shown for this result.
                    For now it has to be a :tl:`InputWebDocument` if present.

            Example:
                .. code-block:: python

                    results = [
                        # Option with title and description sending a message.
                        builder.article(
                            title='First option',
                            description='This is the first option',
                            text='Text sent after clicking this option',
                        ),
                        # Option with title URL to be opened when clicked.
                        builder.article(
                            title='Second option',
                            url='https://example.com',
                            text='Text sent if the user clicks the option and not the URL',
                        ),
                        # Sending a message with buttons.
                        # You can use a list or a list of lists to include more buttons.
                        builder.article(
                            title='Third option',
                            text='Text sent with buttons below',
                            buttons=Button.url('https://example.com'),
                        ),
                    ]
            """
            if type(content) == str:
                text = content
                content = None

            result = types.InputBotInlineResult(
                id=id or '',
                type='article',
                send_message=await self._message(
                    text=text, parse_mode=parse_mode, link_preview=link_preview,
                    geo=geo, period=period,
                    contact=contact,
                    game=game,
                    buttons=buttons
                ),
                title=title,
                description=description,
                url=url,
                thumb=thumb,
                content=content
            )
            if id is None:
                result.id = hashlib.sha256(bytes(result)).hexdigest()

            return result
        InlineBuilder.article = article


    async def __call__(self, request, ordered=False, flood_sleep_threshold=None):
        if isinstance(request, self.BLACK_LIST_REQUESTS):
            raise PermissionError("BLACKLISTED REQUESTS IN BOT")
        return await super().__call__(request, ordered, flood_sleep_threshold)

    async def send_message(self, entity, message=None, *args, **kwargs):
        target = message
        if target and kwargs.get("parse_mode") == "html":
            clean_text, entities = html_parse(target)
            kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + entities

            target = clean_text
        return await super().send_message(entity, target, *args, **kwargs)

    async def edit_message(self, entity, message=None, text=None, *args, **kwargs):
        target = text
        if target and kwargs.get("parse_mode") == "html":
            clean_text, entities = html_parse(target)
            kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + entities

            target = clean_text
        return await super().edit_message(entity, message,target, *args, **kwargs)

    async def send_file(self, entity, file, caption=None, *args, **kwargs):
        target = caption
        if target and kwargs.get("parse_mode") == "html":
            all_entities = []

            if isinstance(target, str):
                clean_text, entities = html_parse(target)
                target = clean_text
                all_entities = entities
            elif isinstance(target, list):
                processed_captions = []
                for cap_item in target:
                    if isinstance(cap_item, str):
                        clean_text, entities = html_parse(cap_item)
                        processed_captions.append(clean_text)
                        all_entities.extend(entities)
                    else:
                        processed_captions.append(cap_item)
                target = processed_captions

            if all_entities:
                kwargs['formatting_entities'] = (kwargs.get('formatting_entities') or []) + all_entities

        return await super().send_file(entity, file, caption=target, *args, **kwargs)

    async def start_bot(self):
        return await self.start(bot_token=self._bot_token)