from utils import *
import json
from data.item.Data import Data
from data.attachments.Attachment import Attachment
from .Likes import FetchLikes
from .ObjectFetcher import ObjectFetcher


class Comment(Data):
    def __init__(self, api, comment, progress, dlg_id, options):
        super().__init__(progress, dlg_id, options)
        self.vk_comment = comment
        self.api = api
        self.likes = None

    def to_json(self, ctx):
        vk_comment = self.vk_comment
        # write message head
        exported_comment = {
            'type': __class__.__name__.lower(),
            'date': vk_comment.get('date', 0),
            'text': vk_comment.get('text', ''),
            'reply_to_user': vk_comment.get('reply_to_user', 0),
            'reply_to_comment': vk_comment.get('reply_to_comment', 0),
        }

        sender_id = vk_comment.get('from_id', 0)
        ctx.add_user(sender_id, self)

        exported_comment['sender'] = {
            'id': sender_id
        }

        # handle attachments
        if 'attachments' in vk_comment:
            exported_comment['attachments'] = \
                Attachment.attachments_to_json(ctx, vk_comment['attachments'], [self.progress, self.id, self.options])

        # handle likes
        if vk_comment['likes']['count'] > 0:
            self.likes = FetchLikes(self.api, self.id, __class__.__name__.lower(),
                                    vk_comment.get('id', 0), self.options)
            vk_comment['likes'] = self.likes.get_json(ctx)

        if self.options.arguments.save_raw:
            exported_comment['raw'] = vk_comment

        return exported_comment

    def to_html(self, ctx, comment):
        sender_id = comment['sender']['id']
        sender = ctx.get_user(sender_id)

        # Attachments block
        attach_block = ''
        if 'attachments' in comment:
            attach_block = Attachment.attachments_to_html(ctx, comment['attachments'], [self.progress, self.id, self.options])

        # Likes block
        likes_block = ''
        if self.likes:
            likes_block = self.likes.get_html_body(ctx, self.progress)

        return '''
        <div class="comment comment--level-{level}" data-json='{json}'>
            <div class="comment-head">
                <div class="comment-head__photo-block">
                    <img class="comment-head__photo" src="{sender_photo}" />
                </div>
                <div class="comment-head__info">
                    <a class="comment-head__profile" href="{sender_profile}" title="{sender_fullname}">{sender_firstname}</a>
                    <div class="comment-head__date-block">
                        <span class="comment-head__date">{date}</span>
                    </div>
                </div>
            </div>
            <div class="comment-body">
                <div class="comment-text">
                    {text}
                </div>
                {attach_block}
                {likes_block}
             </div>
        </div>
        '''.format(**{
            'level': ctx.level,
            'sender_profile': sender['link'],
            'sender_fullname': sender['name'],
            'sender_firstname': sender['first_name'],
            'sender_photo': sender['filename'],
            'date': fmt_timestamp(comment['date']),
            'text': comment['text'],
            'attach_block': attach_block,
            'likes_block': likes_block,
            'json': json.dumps(comment, ensure_ascii=False) if self.options.arguments.save_json_in_html else ''
        })


class FetchComments(ObjectFetcher):
    def __init__(self, api, vk_id, post_id, options):
        super().__init__(api, vk_id, options)
        self.post_id = post_id

    def _getArrayApiCall(self, offset, count):
        return self.api.call('wall.getComments', [
                ('offset', offset),
                ('count', count),
                ('owner_id', self.id),
                ('post_id', self.post_id),
                ('rev', 1)
            ])

    def _create_object(self, item_data, progress, vk_id, options):
        return Comment(item_data, progress, vk_id, options)

    def _html_frame(self, options):
        return '''
            <div class="comments">
            {data}
            </div>
            '''
