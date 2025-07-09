from .models import Chat, ChatParticipant


def create_chat(name: str, is_group: bool, user_ids: list[int]) -> Chat:
    chat = Chat.objects.create(name=name, is_group=is_group)

    participants = [ChatParticipant(chat=chat, user_id=uid) for uid in user_ids]
    ChatParticipant.objects.bulk_create(participants)

    return chat
