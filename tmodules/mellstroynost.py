from loader import command, watcher, ENM


class mellnost():
    def __init__(self):
        self.name = "Mellstroynost"
        self.description = "Мелстройность"
        self.version = "rA9"
        self.mode = False


    @command("mell")
    async def mell(self,e: ENM):
        self.mode = not self.mode
        self.db.set("enabled",self.mode)
        await e.edit(f"Режимость меллстройность {self.mode}")

    @watcher(outgoing=True)
    async def watch(self,e:ENM):
        if self.db.get("enabled",self.mode):
            await e.edit(self.nostb(e.raw_text))

    def nostb(self,text):
        texte = text.split()
        out = ""
        for i in texte:
            if len(i) >1:
                out += self.rekurse(i)

        return out


    def rekurse(self,i):
        out = ""
        if i[-1].lower() in ["о", "а", "ы", "я", "у", "е", "э", "и"]:
            out += i + "сть"
        elif i[-1] in ["!", ".", "?"]:
            out += i[0:-1] + self.rekurse(i[0:-1].replace("!","").replace(".","").replace("?","")) + i[-1]
        else:
            out += i + "ость"
        return out