from loader import command, ENM, watcher

class EchoMod:
     def __init__(self):
         self.name = "Okak"
         self.description = "Окак модуль"
         self.version = "1.0"
         self.enl = False

     @watcher(sticker=False, incoming=False)
     async def watcher(self, m: ENM):
         print(m._entities)
         if self.enl and m.raw_text != ".okak":
             await m.edit("окак "*len(m.raw_text.split()))

     @command("okak")
     async def okak(self,m:ENM):
         self.enl = not self.enl
         if self.enl:
             await m.edit("[👍](tg://emoji?id=5276441836523636642)ACTIVATED", parse_mode='md')
         else:
             await m.edit("не не окак <emoji document_id=5276441836523636642>😎</emoji>", parse_mode='html')
