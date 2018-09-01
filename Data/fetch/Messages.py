from .ObjectFetcher import ObjectFetcher
from data.item.Message import Message


MSG_MERGE_TIMEOUT = 60 * 5 # two sequential messages from the same sender are going to be merged into one if sent in this time range


class FetchMessages(ObjectFetcher):
    def __init__(self, api, conversation, options):
        self.type = conversation['peer']['type']
        self.id = conversation['peer']['id'] if self.type == 'user' else conversation['peer']['local_id']
        super().__init__(api, self.id, options)

    def _getArrayApiCall(self, offset, count):
        selector = 'user_id' if self.type == 'user' else 'peer_id'

        return self.api.call('messages.getHistory', [
                ('offset', offset),
                ('count', count),
                (selector, self.id),
                ('rev', 1)
            ])

    def _create_object(self, item_data, progress, vk_id, options):
        return Message(item_data, progress, vk_id, options)

    def _html_frame(self, options):
        return '''
            <div class="messages">
            {data}
            </div>
            '''
