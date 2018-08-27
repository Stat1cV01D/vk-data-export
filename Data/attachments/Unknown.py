# We don't inherit Attachment class so it won't be in "known" list
class Unknown:
    def __init__(self, attachment):
        self.type = attachment['type']

    def to_json(self, context, attachment):
        return {
            'type': self.type
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-{type}">
            <span class="attach-{type}__title">{title}</span>
            <div class="attach-{type}__data">{data}</div>  
        </div>
        '''.format(**{
            'type': self.type,
            'title': "Unknown attachment type",
            'data': attach
        })
