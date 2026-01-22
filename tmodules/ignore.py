from loader import command, ENM, watcher


class Ignore:
    def __init__(self):
        self.name = "Ignore"
        self.description = ".setchat ID \n Удаляет сообщения от этого человека"
        self.version = "1.0"
        self.target_id = None

    @watcher(outgoing=False,incoming=True)
    async def dels(self,e: ENM):
        if e.sender_id == self.target_id and self.target_id:
            await e.message.delete()

    @command(cmd="setchat",aliases=["sc"])
    async def sc(self,e:ENM):
        flargs = e.raw_text.split()
        if len(flargs) != 2: await e.edit("Необходим 1 аргумент: ID/Username/Phone")
        ent = await e._client.get_entity(flargs[1])
        self.target_id = ent.id

        await e.edit(f"Установлен юзер: {self.target_id}")