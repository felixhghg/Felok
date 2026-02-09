import asyncio
import json
import os
import base64
from cipher import encrypt_data, decrypt_data


class Database:
    def __init__(self, owner: str):
        self.__filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.json")
        self.__owner = owner.lower()

        self.RANK_HOST = 10
        self.RANK_OWNER = 8
        self.RANK_SPECIAL = 4
        self.RANK_CONTACT = 2
        self.RANK_GUEST = 0

    def __read_all(self) -> dict:
        if not os.path.exists(self.__filepath): return {}
        try:
            with open(self.__filepath, "rb") as f:
                blob = f.read()
                decrypted = decrypt_data(base64.b64decode(blob))
                return json.loads(decrypted)
        except Exception:
            return {}

    def __write_all(self, data: dict):
        try:
            print(data)
            json_str = json.dumps(data,default=list)
            print(json_str)
            encrypted = base64.b64encode(encrypt_data(json_str))
            with open(self.__filepath, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            print(f"save bd err: {e}")

    def set(self, key: str, value):
        all_data = self.__read_all()
        if self.__owner not in all_data: all_data[self.__owner] = {}
        all_data[self.__owner][key] = value
        self.__write_all(all_data)

    def get(self, key: str, default=None):
        all_data = self.__read_all()
        return all_data.get(self.__owner, {}).get(key, default)

    def clear(self):
        all_data = self.__read_all()
        if self.__owner in all_data:
            del all_data[self.__owner]
            self.__write_all(all_data)

    def items(self):
        all_data = self.__read_all()
        return all_data.get(self.__owner, {}).items()

    def get_rank(self, event) -> int:
        if event.out:
            return self.RANK_HOST

        uid = event.sender_id
        all_data = self.__read_all()
        sec = all_data.get("security", {})

        if uid in sec.get("owners", []): return self.RANK_OWNER
        if uid in sec.get("special", []): return self.RANK_SPECIAL

        sender = event.sender

        if getattr(sender, 'contact', False):
            return self.RANK_CONTACT

        return self.RANK_GUEST



    def check_access(self, event, min_rank: int) -> bool:
        return self.get_rank(event) >= min_rank
