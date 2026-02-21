# Idea by @kilka_let_me_cry
import asyncio
import random

from loader import watcher, ENM

class mazhir():
    def __init__(self):
        self.name = "ZHIIR"
        self.description = "zhir, Idea by @kilka_let_me_cry"
        self.version = "very zhir"

    @watcher(incoming=True)
    async def mamochkaIILI(self,e:ENM):
        if "momkin_zhir" in e.raw_text:
            await e.reply("Готовлю жир по цене...")
            await asyncio.sleep(random.randint(3,4))
            await e.reply("Впитываю цену за единицу в пузо...")
            await asyncio.sleep(random.randint(3, 4))
            await e.reply("<u>- СИСТЕМА: Жир успешно впитан в бока. Поздравляю, Феландр! -</u>",parse_mode="HTML")
