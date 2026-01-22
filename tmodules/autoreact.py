from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

from loader import ENM,command,watcher

class AutoReact():
    def __init__(self):
        self.name = "AutoReact"
        self.description = "Auto React on new messages in chat\nUsage: .arsc [ID/Username/Phone] [Emoji]"
        self.version = "-1"
        self.entity_id = None
        self.emoji = None

    @command(cmd = "arsc")
    async def arsc(self, e: ENM):
        flargs = e.raw_text.split()
        if len(flargs) != 3: await e.edit("2 arguments needed: ID/Username/Phone Emoji")
        ent = await e._client.get_entity(flargs[1])
        self.entity_id = ent.id
        self.emoji =flargs[2]
        await e.edit(f"Set chat: {ent.id}")

    @watcher(outgoing=True,incoming=True)
    async def watcher(self,e:ENM):
        if self.entity_id and e.chat_id == self.entity_id and self.emoji:
            await e._client(SendReactionRequest(peer=e.chat_id,msg_id=e._message_id,reaction=[ReactionEmoji(emoticon=self.emoji)]))