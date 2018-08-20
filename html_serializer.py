from exporter import *
import codecs


class HTMLOutput:
    def __init__(self):
        self.data = []

    def append(self, text):
        self.data.append(text)

    def get(self):
        return ''.join(self.data)


class HTMLSerializerContext:
    def __init__(self, progress, output, export_ctx, level=1):
        self.progress = progress
        self.output = output
        self.export_ctx = export_ctx
        self.level = level
        self.prev_merge_sender = None
        self.prev_merge_msg_timestamp = 0

    def next_level(self):
        return HTMLSerializerContext(self.progress, self.output, self.export_ctx, self.level + 1)

    def get_user(self, user_id):
        return self.export_ctx.users.get(user_id, None)

    def user_exists(self, user_id):
        return user_id in self.export_ctx.users

class HTMLSerializer:
    def __init__(self, api, options):
        self.options = options
        self.api = api
        self.user_fetcher = UserFetcher(api)
        self.export_ctx = ExportContext(self.user_fetcher)
        self.serializer_ctx = None

    @property
    def extension(self):
        return "html"

    def serialize(self, data_container, progress):
        # load stylesheet early
        with codecs.open('style.css', 'r', encoding='utf-8') as f:
            stylesheet = f.read()

        files = dict()
        self.serializer_ctx = HTMLSerializerContext(progress, HTMLOutput(), self.export_ctx)

        if self.options.arguments.embed_resources:
            link_block = '<style>{stylesheet}</style>'.format(stylesheet=stylesheet)
        else:
            link_block = '<link rel="stylesheet" href="style.css" />'
            files['style.css'] = stylesheet

        self.serializer_ctx.output.append('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            {link_block}
        </head>
        <body>
        '''.format(link_block=link_block))
        data_container.get_html_body(self.export_ctx, self.serializer_ctx, progress)
        self.serializer_ctx.output.append('</body></html>')

        return {
            'text': self.serializer_ctx.output.get(),
            'files': files
        }
