from loader import command, ENM, ECQ
from inline import InlineButton,send_buttons

class Inliner():
    def __init__(self):
        self.name = "Clicker"
        self.description = "Clicker, to start .clck"
        self.version = "lol"
        self.clcks = 0

    async def add_clck(self,event: ECQ):
        self.clcks +=1
        await event.edit(f"Количество кликов по кнопке: {self.clcks}",buttons=[InlineButton(text="Клик!",callfunc=self.add_clck).button])

    @command("clck")
    async def clck(self,event: ENM):
        chat = await event.get_input_chat()
        await send_buttons(chat,text=f"Количество кликов по кнопке: {self.clcks}",buttons=[InlineButton(text="Клик!",callfunc=self.add_clck)])

        await event.message.delete()