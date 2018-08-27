from utils import *
from .Attachment import Attachment


class Page(Attachment):
    def to_json(self, context, page):
        return {
            'type': __class__.__name__.lower(),
            'group_id': page.get('group_id', 0),
            'title': page.get('title', 0),
            'created': page.get('created', ''),
            'view_url': page.get('view_url', 0),
            'views': page.get('views', {}).get('count', 0)
        }

    def to_html(self, ctx, attach):
        args = {**attach, **{
            'created': fmt_timestamp(attach['created'])
        }}

        return '''
        <div class="attach attach-page">
            <div class="attach-page__title">{title}</div>
            <a class="attach-page__link" href="{view_url}"></a>
        </div>
        '''.format(**args)
