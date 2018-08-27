from html_serializer import HTMLSerializer
from Data.Message import Message

MSG_MERGE_TIMEOUT = 60 * 5 # two sequential messages from the same sender are going to be merged into one if sent in this time range


class ExportMessages:
    def __init__(self, api, dlg_type, dlg_id, options):
        self.api = api
        self.type = dlg_type
        self.id = dlg_id
        self.attach_dir = str(self.id)
        self.output_dir = options.output_dir
        self.options = options
        # The core list of Message objects
        self.messages = []

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

    def get_data(self, progress, use_existing=True):
        if not self.messages or not use_existing:
            cur_step = 0
            self.messages = []
            for msg, total in self.fetch_messages():
                progress.update(cur_step, total)
                cur_step += 1
                self.messages.append(Message(msg, progress, self.id, self.options))
        return self.messages

    def get_html_body(self, export_ctx, serializer_ctx, progress):
        self.get_data(progress)
        cur_step = 0
        total = len(self.messages)
        progress.update(cur_step, total)

        serializer_ctx.output.append('<div class="messages">')
        for obj in self.messages:
            cur_step += 1
            progress.update(cur_step, total)
            serializer_ctx.output.append(obj.to_html(serializer_ctx, obj.to_json(export_ctx)))
        serializer_ctx.output.append('</div>')
