from loader import command, ENM

RANKNAMES = {
    0: "Остальные",
    2: "Контакты",
    4: "Определенные",
    8: "Владельцы",
    10: "Хост",
    "owners": "Владельцы",
    "special": "Определенные"
}

class Security:
    def __init__(self):
        self.name = "Security"
        self.description = "builtin модуль"
        self.version = "1.0"

    @command("cha", rank=0)
    async def check_access(self, e: ENM):

        rank = self.db.get_rank(e)
        await e.reply(
            f"<emoji document_id=5920344347152224466>👤</emoji> Вы находитесь в группе:{RANKNAMES[rank]}({rank})",
            parse_mode="html")

    # owners
    @command("addowner",rank=8)
    async def addowner(self,e:ENM):
        args = e.raw_text.split()
        entity = None
        if len(args) == 2:
            entity = await e._client.get_entity(args[1])
        elif e.message.reply_to_msg_id:
            reply_msg = await e.get_reply_message()
            entity = await e._client.get_entity(reply_msg.sender_id)
        else:
            await e.edit(f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Ответьте с реплаем или с аргументом",
                         parse_mode="html")
            return
        owns = self.db.get("owners",[])
        if type(owns) == list:
            if entity.id in owns:
                await e.edit(
                    f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Данный пользователь уже в группе Владельца",
                    parse_mode="html")
                return
            owns.append(entity.id)
        else:
            owns = [entity.id]
        self.db.set("owners",owns)
        await e.edit(f"<emoji document_id=5256143829672672750>👤</emoji> {entity.id} добавлен в группу: Владельцы",parse_mode="html")


    @command("remr", rank=8)
    async def remgroup(self, e: ENM):
        args = e.raw_text.split()
        entity = None
        if len(args) == 2:
            entity = await e._client.get_entity(args[1])
        elif e.message.reply_to_msg_id:
            reply_msg = await e.get_reply_message()
            entity = await e._client.get_entity(reply_msg.sender_id)
        else:
            await e.edit(
                f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Ответьте с реплаем или с аргументом",
                parse_mode="html")
            return



        k = ""
        for i in ["owners","special"]:
            owns = self.db.get(i,[])
            if entity.id in owns:
                k = i
                break

        if entity.id not in owns:
            await e.edit(
                f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Данный пользователь ни в какой либо группе",
                parse_mode="html")
            return
        if type(owns) == list:
            owns.remove(entity.id)
        else:
            owns = []

        self.db.set(k, owns)
        await e.edit(f"<emoji document_id=5256143829672672750>👤</emoji> {entity.id} удален из группы: {RANKNAMES[k]}",
                     parse_mode="html")


    #special
    @command("addspecial", rank=8)
    async def addspec(self, e: ENM):
        args = e.raw_text.split()
        entity = None
        if len(args) == 2:
            entity = await e._client.get_entity(args[1])
        elif e.message.reply_to_msg_id:
            reply_msg = await e.get_reply_message()
            entity = await e._client.get_entity(reply_msg.sender_id)
        else:
            await e.edit(
                f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Ответьте с реплаем или с аргументом",
                parse_mode="html")
            return
        owns = self.db.get("special", [])
        if type(owns) == list:
            if entity.id in owns:
                await e.edit(
                    f"<emoji document_id=5260342697075416641>❌</emoji> Ошибка: Данный пользователь уже в группе Специальные",
                    parse_mode="html")
                return
            owns.append(entity.id)
        else:
            owns = [entity.id]
        self.db.set("special", owns)
        await e.edit(f"<emoji document_id=5256143829672672750>👤</emoji> {entity.id} добавлен в группу: Специальные",
                     parse_mode="html")
