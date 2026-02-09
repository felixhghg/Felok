from loader import command, ENM, ECQ, query, EIQ
from inline import InlineButton, send_buttons


class Inliner():
    def __init__(self):
        self.name = "Clicker"
        self.description = "Clicker, to start .clck"
        self.version = "lol"
        self.clcks = 0

    async def add_clck(self, event: ECQ):
        self.clcks += 1
        await event.edit(f"Количество кликов по кнопке: {self.clcks}",
                         buttons=[InlineButton(text="Клик!", callfunc=self.add_clck).button])

    @command("clck")
    async def clck(self, event: ENM):
        chat = await event.get_input_chat()
        await send_buttons(chat, text=f"Количество кликов по кнопке: {self.clcks}",
                           buttons=[InlineButton(text="Клик!", callfunc=self.add_clck)])

        await event.message.delete()

    @command("test")
    async def t(self, event: ENM):
        await send_buttons(event.chat_id, "Тест",
                           [[InlineButton(text="1 1", callback="1"), InlineButton(text="2 1", callback="2"),
                             InlineButton(text="3 1", callback="3")],
                            [InlineButton(text="1 2", callback="1")],
                            [InlineButton(text="1 3", callback="1"), InlineButton(text="2 3", callback="2")]])

    async def felok_repo(self,e: ECQ):
        await e.edit("Репозиторий Felok находится на сайте гитхаб",buttons=[InlineButton(text="GITHUB", url="https://github.com/felixhghg/Felok").button])

    @query(rank=0)
    async def inl(self, e: EIQ):
        b = e.builder
        return [b.article("Это же.. Inline test","Модуль для Felok??",content="Felok userbot - Довольно сырой на данный момент ЮБ",buttons=[[InlineButton("Репозиторий",callfunc=self.felok_repo).button]])]
