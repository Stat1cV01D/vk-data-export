from utils import *
from .Attachment import Attachment


class Video(Attachment):
    def to_json(self, context, video):
        video_thumb = self.download_image(video)

        context.add_user(video.get('owner_id', 0), self)

        return {
            'type': __class__.__name__.lower(),
            'description': video.get('description', ''),
            'url': "https://vk.com/video%s_%s" % (video.get('owner_id', 0), video.get('id', 0)),
            'title': video.get("title", ''),
            'duration': video.get("duration", 0),
            'views': video.get('views', 0),
            'comments': video.get('comments', 0),
            'thumbnail_filename': video_thumb,
            'platform': video.get('platform', '?'),
            'date': video.get('date', 0),
            'owner_id': video.get('owner_id', 0)
        }

    def to_html(self, ctx, attach):
        args = {**attach, **{
            'duration': fmt_time(attach['duration']),
            'date': fmt_timestamp(attach['date'])
        }}

        uploader_profile = ''
        owner_id = attach['owner_id']
        if ctx.user_exists(owner_id):
            uploader_profile = '<a href="{link}">{name}</a>'.format(**ctx.get_user(owner_id))

        args['uploader_profile'] = uploader_profile

        return '''
        <div class="attach attach-video">
            <a class="attach-video__link" href="{url}" title="{title}">
                <img class="attach-video__thumbnail" src="{thumbnail_filename}" alt="{title}" />
                <div class="attach-video__title">{title}</div>
            </a>
            <div class="attach-video__meta meta">
                <p>Views on VK: <span class="meta__views">{views}, comments on VK: <span class="meta__comments">{comments}</span></p>
                <p>Added at: <span class="meta__date">{date}</span> from {platform} by {uploader_profile}</p>
            </div>
            <div class="attach-video__description">{description}</div>
        </div>
        '''.format(**args)
