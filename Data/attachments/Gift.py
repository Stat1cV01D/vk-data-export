from .Attachment import Attachment


class Gift(Attachment):
    def to_json(self, context, gift):
        gift_thumb = self.download_image(gift, 'thumb_')

        return {
            'type': __class__.__name__.lower(),
            'thumbnail': gift_thumb
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-gift">
            <div class="attach-gift__title">Gift</div>
            <img class="attach-gift__thumbnail" src="{thumbnail}" />
        </div>
        '''.format(**attach)