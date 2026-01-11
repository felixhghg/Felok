import os
from loader import command, install_module, mp, ENM, remove_module


class Loader:
    def __init__(self):
        self.name = "Loader"
        self.description = "builtin модуль для загрузки модулей"
        self.version = "1.0"

    @command("im")
    async def im_cmd(self, event: ENM):
        """Установить модуль"""
        msg = await event.get_reply_message() if event.is_reply else event

        if not msg.file or not msg.file.name.endswith(".py"):
            return await event.edit("❌ Отправь .py файл или ответь на него")

        target_path = os.path.join(mp, msg.file.name.lower())
        await event.edit(f"⏳ Установка `{msg.file.name}`...")

        await msg.download_media(target_path)

        success, meta = install_module(target_path)

        if success:
            await event.edit(
                f"✅ **Модуль загружен**\n"
                f"📦 **Название:** {meta['name']}\n"
                f"📝 **Описание:** {meta['description']}\n"
                f"🔢 **Версия:** {meta['version']}"
            )
        else:
            if os.path.exists(target_path):
                os.remove(target_path)
            if meta == "builtin": await event.edit(f"❌ Попытка перезагрузки встроенного модуля ")
            elif meta == "already": await event.edit(f"❌ Модуль уже установлен")
            else: await event.edit(f"❌ Ошибка при загрузке модуля")




    @command("rm")
    async def rm_cmd(self,event: ENM):
        """Удалить модуль"""

        args = event.raw_text.split(maxsplit=1)
        if len(args) <2:
            return await event.edit("❌ **Введите имя модуля**")

        mn = args[1]

        rm = remove_module(mn)
        if rm and rm != "builtin":
            await event.edit(f"✅ **Модуль {mn} выгружен**")
        elif rm == "builtin":
            await event.edit(f"❌ **Модуль {mn} встроенный**")
        else:
            await event.edit(f"❌ **Модуль {mn} не найден**")


    @command("me")
    async def me_cmd(self,event: ENM):
        """Экспорт модуля"""
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            return await event.edit("❌ **Введите имя модуля для экспорта**")

        mn = args[1].lower()
        fp = os.path.join(mp, f"{mn}.py")
        if os.path.exists(fp):
            await event.edit(f"📤 **Экспортирую** `{mn}`...")
            try:
                await event._client.send_file(event.chat_id, fp, caption=f"📦 Модуль: `{mn}`")
                await event.delete()
            except Exception as e:
                await event.edit(f"❌ **Ошибка при отправке:** `{e}`")
        else:
            await event.edit(f"❌ **Модуль** `{mn}` **не найден**")
