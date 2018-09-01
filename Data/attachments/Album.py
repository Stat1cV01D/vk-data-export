from .Attachment import Attachment


class Album(Attachment):
    def to_json(self, context, album):
        exported_album = {
            'type': __class__.__name__.lower(),
            'description': album.get('text', ''),
            'owner_id': album.get('owner_id', 0),
            'title': album.get('title', 0),
            'date': album.get('created', 0),
            'updated': album.get('updated', 0),
            'id': album.get('id', 0)
        }

        if "items" in album:
            exported_album['items'] = self.attachments_to_json(context.next_level(), album['items'],
                                                               [self.progress, self.id, self.options])

    def to_html(self, ctx, album):
        images_block = ''
        if 'items' in album:
            images_block = self.attachments_to_html(ctx.next_level(), album['items'],
                                                    [self.progress, self.id, self.options])
        return '''
        <div class="attach attach-album">
            <span class="attach-photo__title">{description}</span>
            {images_block}
        </div>
        '''.format(**album, images_block=images_block)
