from .Attachment import Attachment


class Link(Attachment):
    def to_json(self, context, link):
        downloaded = None
        if 'photo' in link:
            downloaded = self.download_image(link['photo'])

        return {
            'type': __class__.__name__.lower(),
            'url': link.get('url', ''),
            'title': link.get('title', ''),
            'caption': link.get('caption', ''),
            'description': link.get('description', ''),
            'filename': downloaded
        }

    def to_html(self, ctx, attach):
        if 'filename' in attach and attach['filename'] is not None:
            return '''
            <div class="attach attach-link">
                <a class="attach-link__link-block" title="{title}" href="{url}">
                    <div class="attach-link__image-block">
                        <img class="attach-link__image" src="{filename}" />
                    </div>
                    <div class="attach-link__description">
                        <div class="attach-link__title">{title}</div>
                        <div class="attach-link__description-text">{description}</div>
                        <div class="attach-link__caption">{caption}</div>
                    </div>
                </a>
            </div>
            '''.format(**attach)
        else:
            return '''
            <div class="attach attach-link">
                <a class="attach-link__link-block attach-link__link-block--no-image" title="{title}" href="{url}">
                    <div class="attach-link__description">
                        <div class="attach-link__title">{title}</div>
                        <div class="attach-link__description-text">{description}</div>
                        <div class="attach-link__caption">{caption}</div>
                    </div>
                </a>
            </div>
            '''.format(**attach)
