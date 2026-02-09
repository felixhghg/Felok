import re

from telethon.tl.types import MessageEntityCustomEmoji


def html_parse(text: str):
    if not text:
        return "", []

    pattern = r'<emoji document_id="?(\d+)"?>(.*?)</emoji>'
    entities = []

    current_text = text

    while True:
        match = re.search(pattern, current_text)
        if not match:
            break

        doc_id = int(match.group(1))
        alt_text = match.group(2)
        start_char_index = match.start()

        before_tag = current_text[:start_char_index]
        utf16_offset = len(before_tag.encode('utf-16-le')) // 2
        utf16_length = len(alt_text.encode('utf-16-le')) // 2

        entities.append(MessageEntityCustomEmoji(
            offset=utf16_offset,
            length=utf16_length,
            document_id=doc_id
        ))


        current_text = current_text[:match.start()] + alt_text + current_text[match.end():]


    return current_text, entities

def html_deparse(text: str, entities: list) -> str:
    """
    Вспомогательная функция для де-парсинга премиум эмодзи(выполняется при отправке любого ENM)
    """
    if not entities:
        return text

    sorted_entities = sorted(entities, key=lambda e: e.offset, reverse=True)

    utf16_text = text.encode('utf-16-le')

    for ent in sorted_entities:
        if isinstance(ent, MessageEntityCustomEmoji):
            start = ent.offset * 2
            end = (ent.offset + ent.length) * 2

            alt_text = utf16_text[start:end].decode('utf-16-le')

            tag = f'<emoji document_id={ent.document_id}>{alt_text}</emoji>'
            tag_utf16 = tag.encode('utf-16-le')

            utf16_text = utf16_text[:start] + tag_utf16 + utf16_text[end:]

    return utf16_text.decode('utf-16-le')