from utils import *
from . import Attachment


class Doc(Attachment):
    def to_json(self, context, doc):
        if 'preview' in doc and 'audio_msg' in doc['preview']:
            return self.handle_voice_msg(context, doc)

        filename = '%s.%s' % (doc.get('id', 0), doc.get('ext', 'unknown'))
        url = doc.get('url', '')

        downloaded = None
        if self.options.arguments.docs and context.depth <= self.options.arguments.docs_depth:
            if url:
                downloaded = self.download_file(url, filename, False, doc.get('size', -1))
            else:
                progress.error("Document [%s] is no more available, skipping\n" % doc.get('title', ''))

        return {
            'type': self.__name__,
            'filename': downloaded,
            'url': url,
            'title': doc.get('title', ''),
            'size': doc.get('size', 0),
            'ext': doc.get('ext', '')
        }

    def to_html(self, ctx, attach):
        args = {**attach, **{
            'filename': attach['filename'] or attach["url"],
            'size': fmt_size(attach['size'])
        }}

        return '''
        <div class="attach attach-doc">
            <a href="{filename}" class="attach-doc__link-block">
                <div class="attach-doc__desc">
                    <div class="attach-doc__link" title="{title}">{title}</div>
                    <div class="attach-doc__size">{size}</div>
                </div>
            </a>
        </div>
        '''.format(**args)