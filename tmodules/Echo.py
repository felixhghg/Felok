from loader import command, ENM

class EchoMod:
     def __init__(self):
         self.name = "Echo"
         self.description = "Test Module"
         self.version = "1.0"

     @command("echo")
     async def echo(self,event:ENM):
          await event.edit(f"Эхо: {event.raw_text}")
