# We don't inherit Attachment class so it won't be in "known" list
class Unknown:
    def __init__(self, options):
        self.options = options

    def to_json(self, context, attachment):
        return {
            'type': attachment['type']
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-{type}">
            <span class="attach-{type}__title">{title}</span>
        </div>
        '''.format(**{
            'type': attach['type'],
            'title': "Unknown attachment type"
        })