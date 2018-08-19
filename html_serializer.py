import codecs


class HTMLOutput:
    def __init__(self):
        self.data = []

    def append(self, text):
        self.data.append(text)

    def get(self):
        return ''.join(self.data)


class HTMLSerializerContext:
    def __init__(self, progress, output, input_json, level):
        self.progress = progress
        self.output = output
        self.input_json = input_json
        self.level = level
        self.prev_merge_sender = None
        self.prev_merge_msg_timestamp = 0

    def next_level(self):
        return HTMLSerializerContext(self.progress, self.output, self.input_json, self.level + 1)


class HTMLSerializer:
    def __init__(self, options):
        self.options = options
        self.ctx = None

    @property
    def extension(self):
        return "html"

    def serialize(self, input_obj, progress):
        input_json = input_obj.to_json(progress)

        # load stylesheet early
        with codecs.open('style.css', 'r', encoding='utf-8') as f:
            stylesheet = f.read()

        self.ctx = HTMLSerializerContext(progress, HTMLOutput(), input_json, 1)
        files = dict()

        if self.options.arguments.embed_resources:
            link_block = '<style>{stylesheet}</style>'.format(stylesheet=stylesheet)
        else:
            link_block = '<link rel="stylesheet" href="style.css" />'
            files['style.css'] = stylesheet

        self.ctx.output.append('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            {link_block}
        </head>
        <body>
            <div class="messages">
        '''.format(link_block=link_block))

        cur_step = 0
        total = len(input_json.get(Class.section_name))

        for msg in input_json.get(Class.section_name):
            if cur_step == 0:
                self.ctx.progress.update(0, total)

            self.ctx.output.append(Class.serialize(self.ctx, msg))

            cur_step += 1
            self.ctx.progress.update(cur_step, total)

            self.ctx.output.append('</div></body></html>')

        return {
            'text': self.ctx.output.get(),
            'files': files
        }
