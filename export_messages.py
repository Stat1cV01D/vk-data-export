from exporter import *
from html_serializer import HTMLSerializer
from .Data.Message import Message

MSG_MERGE_TIMEOUT = 60 * 5 # two sequential messages from the same sender are going to be merged into one if sent in this time range


class ExportMessages(HTMLSerializer):
    def __init__(self, api, dlg_type, dlg_id, options):
        super().__init__(options)
        self.api = api
        self.type = dlg_type
        self.id = dlg_id
        self.attach_dir = str(self.id)
        self.output_dir = options.output_dir
        self.options = options
        self.user_fetcher = UserFetcher(api)
        self.ctx = ExportContext(self.user_fetcher)

    def fetch_messages(self):
        offset = 0

        selector = 'user_id' if self.type == 'user' else 'peer_id'
        author_id = self.id if self.type == 'user' else (2000000000 + self.id if self.type == 'chat' else -self.id)

        while True:
            messages = self.api.call('messages.getHistory',
                                     [('offset', offset), ('count', 200), (selector, author_id), ('rev', 1)])
            if len(messages['items']) == 0:
                break
            for msg in messages['items']:
                yield (msg, messages['count'])
            offset += len(messages['items'])

    def export_json(self, progress):
        cur_step = 0
        messages = []
        for msg, total in self.fetch_messages():
            if cur_step == 0:
                progress.update(0, total)

            msg_obj = Message(self.api, self.type, self.id, self.options)
            messages.append(msg_obj.to_json(self.ctx, msg))

            cur_step += 1
            progress.update(cur_step, total)

        return messages



