from utils import *
from .Attachment import Attachment


class Wall(Attachment):
    def __init__(self, progress, dlg_id, options, full_export=False):
        super().__init__(progress, dlg_id, options)
        self.full_export = full_export

    def to_json(self, context, wall):
        if 'from_id' in wall:
            context.add_user(wall['from_id'], self)

        if 'to_id' in wall:
            context.add_user(wall['to_id'], self)

        exported_post = {
            'type': __class__.__name__.lower(),
            'from_id': wall.get('from_id', 0),
            'to_id': wall.get('to_id', 0),
            'post_type': wall.get('post_type', ''),
            'date': wall.get('date', 0),
            'text': wall.get('text', ''),
            'url': "https://vk.com/wall%s_%s" % (wall.get('from_id', 0), wall.get('id', 0)),
            'views': wall.get('views', {}).get('count', 0),
            'likes': wall.get('likes', {}).get('count', 0),
            'comments': wall.get('comments', {}).get('count', 0),
            'reposts': wall.get('reposts', {}).get('count', 0),
            'source': wall.get('post_source', {'type': 'api', 'platform': 'unknown'})
        }

        if "attachments" in wall:
            exported_post['attachments'] = self.attachments_to_json(context.next_level(), wall['attachments'],
                                                                    [self.progress, self.id, self.options])

        if "copy_history" in wall:
            # this is a repost
            for repost in wall['copy_history']:
                exported_post['repost'] = []
                post_type = repost.get('post_type', '')
                if post_type == "post":
                    exported_post['repost'].append(self.to_json(context.next_level(), repost))
                else:
                    self.progress.error("No handler for post type: %s\n" % post_type)

        if self.full_export and "comments" in wall:
            pass

        if self.full_export and "likes" in wall:
            pass

        return exported_post

    def to_html(self, ctx, attach):
        args = {**attach, **{
            'date': fmt_timestamp(attach['date'])
        }}

        attach_block = ''
        if 'attachments' in attach:
            attach_block += self.attachments_to_html(ctx, attach['attachments'], [self.progress, self.id, self.options])

        if len(attach_block) > 0:
            attach_block = '<div class="msg-attachments">{attach_block}</div>'.format(attach_block=attach_block)

        args['attach_block'] = attach_block

        head_block = ''
        if 'from_id' in attach and ctx.user_exists(attach['from_id']):
            user_data = ctx.get_user(attach['from_id'])
            if 'filename' in user_data:
                head_block = '''
                <div class="post-head">
                    <div class="post-head__image-block">
                        <img class="post-head__image" src="{filename}" />
                    </div>
                    <div class="post-head__info">
                        <div class="post-head__name">
                            <a class="post-head__link" href="{link}">{name}</a>
                        </div>
                        <div class="post-head__date">{date}</div>
                    </div>
                </div>
                '''.format(**user_data, date=args['date'])
            else:
                head_block = '''
                <div class="post-head">
                    <div class="post-head__name">
                        <a class="post-head__link" href="{link}">{name}</a>
                    </div>
                    <div class="post-head__date">{date}</div>
                </div>
                '''.format(**user_data, date=args['date'])

        args['head_block'] = head_block

        repost_block = ''
        if 'repost' in attach:
            for repost in attach['repost']:
                repost_block = '''
                <div class="attach-post__repost">
                    {repost_block}
                </div>
                '''.format(repost_block=self.to_html(ctx, repost))

        args['repost_block'] = repost_block

        return '''
        <div class="attach attach-post">
            {head_block}
            <div class="attach-post__text">{text}</div>
            <a class="attach-post__link" href="{url}"></a>
            {attach_block}
            {repost_block}
        </div>
        '''.format(**args)
