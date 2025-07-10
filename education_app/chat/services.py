from .models import Chat, ChatParticipant


class ChatService:
    @staticmethod
    def create_chat(name: str, is_group: bool, user_ids: list[int]) -> Chat:
        chat = Chat.objects.create(name=name, is_group=is_group)

        participants = [ChatParticipant(chat=chat, user_id=user_id) for user_id in user_ids]
        ChatParticipant.objects.bulk_create(participants)

        return chat

    @staticmethod
    def update_chat(instance: Chat, name: str, is_group: bool, user_ids: list[int]) -> Chat:
        instance.name = name
        instance.is_group = is_group
        instance.save()

        ChatParticipant.objects.filter(chat=instance).delete()
        ChatParticipant.objects.bulk_create([
            ChatParticipant(chat=instance, user_id=uid) for uid in user_ids
        ])

        return instance