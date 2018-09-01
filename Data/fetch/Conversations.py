from .ObjectFetcher import ObjectFetcher
from data.item.Conversation import Conversation


MSG_MERGE_TIMEOUT = 60 * 5 # two sequential messages from the same sender are going to be merged into one if sent in this time range


class FetchConversations(ObjectFetcher):
    def __init__(self, api, options):
        super().__init__(api, api.user_id, options)

    def _getCoversationById(self, chat_type, chat_id):
        # There can be several IDs separated by comma
        chat_id = chat_id if chat_type == 'user' else (2000000000 + self.id if chat_type == 'chat' else -self.id)

        return self.api.call('messages.getConversationsById', [
            ('peer_ids', chat_id)
        ])

    def _getArrayApiCall(self, offset, count):
        if self.options.arguments.person is not None:
            return self._getCoversationById('user', self.options.arguments.person)
        elif self.options.arguments.chat is not None:
            return self._getCoversationById('chat', self.options.arguments.chat)
        elif self.options.arguments.group is not None:
            return self._getCoversationById('group', self.options.arguments.group)
        else:
            return self.api.call('messages.getConversations', [
                ('offset', offset),
                ('count', count)
            ])

    def _create_object(self, item_data, progress, vk_id, options):
        return Conversation(item_data, progress, vk_id, options)

    def _html_frame(self, options):
        return '''
            <div class="messages">
            {data}
            </div>
            '''
