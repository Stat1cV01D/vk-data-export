import json
from data.item.Data import Data
from data.fetch.Messages import FetchMessages


class Conversation(Data):
    def __init__(self, api, conversation, progress, options):
        super().__init__(progress, -1, options)
        self.vk_conversation = conversation
        self.api = api
        self.messages = None

    def to_json(self, ctx):
        vk_conversation = self.vk_conversation
        export_data = {}
        self.messages = FetchMessages(self.api, vk_conversation, self.options)
        return export_data

    def to_html(self, ctx, post):
        pass


