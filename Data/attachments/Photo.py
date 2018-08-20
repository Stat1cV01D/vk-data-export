from .Attachment import Attachment


class Photo(Attachment):
    def to_json(self, context, photo):
        downloaded = self.download_image(photo)
        return {
            'type': __class__.__name__.lower(),
            'filename': downloaded,
            'url': self.find_largest(photo),
            'description': photo.get('text', ''),
            'owner_id': photo.get('owner_id', 0),
            'width': photo.get('width', 0),
            'height': photo.get('height', 0),
            'date': photo.get('date', 0),
            'id': photo.get('id', 0),
            'album_id': photo.get('album_id', 0)
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-photo">
            <span class="attach-photo__title">{description}</span>
            <img class="attach-photo__image" src="{filename}" alt="{description}" />
        </div>
        '''.format(**attach)