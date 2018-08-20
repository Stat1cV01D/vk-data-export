from .Attachment import Attachment


class Sticker(Attachment):
    def to_json(self, context, sticker):
        # find the largest sticker image file
        largest = None
        if 'images' in sticker:
            for image in sticker['images']:
                if largest is None or image['width'] > largest['width']:
                    largest = image

        url = largest['url'] if largest is not None else ''

        downloaded = self.download_file(url, str(sticker.get('sticker_id', 0)), True) if largest is not None else None

        return {
            'type': __class__.__name__.lower(),
            'filename': downloaded,
            'url': url
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-sticker">
            <img class="attach-sticker__image" src="{filename}" />
        </div>
        '''.format(**attach)