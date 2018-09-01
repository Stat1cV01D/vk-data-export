class ObjectFetcher:
    def __init__(self, api, vk_id, options):
        self.api = api
        self.id = vk_id
        self.options = options
        # The core list of Message objects
        self.data_items = []

    # stubs, to be overridden in subclasses
    def _getArrayApiCall(self, offset, count):
        return {
            'items': [],
            'count': 0
        }

    def _create_object(self, item_data, progress, vk_id, options):
        return None

    def _html_frame(self, options):
        return '{data}'

    # Core functions
    def fetch_data_items(self):
        offset = 0

        while True:
            messages = self._getArrayApiCall(offset, 200)
            if len(messages['items']) == 0:
                break
            for msg in messages['items']:
                yield (msg, messages['count'])
            offset += len(messages['items'])

    def get_data(self, progress, use_existing=True):
        if not self.data_items or not use_existing:
            cur_step = 0
            self.data_items = []
            for msg, total in self.fetch_data_items():
                progress.update(cur_step, total)
                cur_step += 1
                self.data_items.append(self._create_object(msg, progress, self.id, self.options))
        return self.data_items

    def get_json(self, export_ctx, progress):
        self.get_data(progress)
        result_json = []
        for obj in self.data_items:
            result_json.append(obj.to_json(export_ctx))
        return result_json

    def get_html_body(self, serializer_ctx, progress):
        self.get_data(progress)
        cur_step = 0
        total = len(self.data_items)
        progress.update(cur_step, total)
        data = ""
        for obj in self.data_items:
            cur_step += 1
            progress.update(cur_step, total)
            data += obj.to_html(serializer_ctx, obj.to_json(serializer_ctx.export_ctx))
        serializer_ctx.output.append(self._html_frame(self.options).format(**{'data': data}))
