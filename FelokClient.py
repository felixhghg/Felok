from telethon import TelegramClient, functions
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError, CodeInvalidError, \
    PhoneCodeInvalidError


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
        self._session = session
        self._bsession: FelokBot | None = None
        self.prefix = "."

        super().__init__(session, api_id, api_hash, device_model="F 64bit",system_version="F1",app_version="5.1.7",lang_code="ru",system_lang_code="ru")



    async def __call__(self, request, ordered= False,flood_sleep_threshold=None):
        if isinstance(request,self.BLACK_LIST_REQUESTS):
            raise PermissionError("BLACKLISTED REQUESTS")

        return await super().__call__(request,ordered,flood_sleep_threshold,)

    async def start_ub(self):
        await self.connect()

        if not await self.is_user_authorized():
            await self.send_code_request(str(self.phone))
            return "code"


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

    async def __call__(self, request, ordered=False, flood_sleep_threshold=None):
        if isinstance(request, self.BLACK_LIST_REQUESTS):
            raise PermissionError("BLACKLISTED REQUESTS IN BOT")
        return await super().__call__(request, ordered, flood_sleep_threshold)

    async def start_bot(self):
        return await self.start(bot_token=self._bot_token)