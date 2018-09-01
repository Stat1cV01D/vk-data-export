from utils import *
import json
from data.item.Data import Data
from data.attachments.Attachment import Attachment


MSG_MERGE_TIMEOUT = 60 * 5 # two sequential messages from the same sender are going to be merged into one if sent in this time range


class Message(Data):
    def __init__(self, msg, progress, dlg_id,  options):
        super().__init__(progress, dlg_id, options)
        self.vk_msg = msg

    def to_json(self, ctx):
        vk_msg = self.vk_msg
        # write message head
        exported_msg = {
            'date': vk_msg.get('date', 0),
            'message': vk_msg.get('text', ''),
            'is_important': vk_msg.get('important', False),
            'is_updated': 'update_time' in vk_msg and vk_msg['update_time']
        }

        is_updated = False
        if 'update_time' in vk_msg and vk_msg['update_time']:
            is_updated = True
            exported_msg['updated_at'] = vk_msg['update_time']
        exported_msg['is_updated'] = is_updated

        sender_id = vk_msg.get('from_id', 0) or vk_msg.get('user_id', 0)
        ctx.add_user(sender_id, self)

        exported_msg['sender'] = {
            'id': sender_id
        }

        # handle forwarded messages
        if len(vk_msg.get('fwd_messages', [])) > 0:
            exported_msg['forwarded'] = []
            for fwd_msg in vk_msg['fwd_messages']:
                exported_msg['forwarded'].append(__class__(fwd_msg, self.progress, self.id, self.options).to_json(ctx))

        # handle attachments
        if 'attachments' in vk_msg:
            exported_msg['attachments'] = \
                Attachment.attachments_to_json(ctx, vk_msg['attachments'], [self.progress, self.id, self.options])

        if 'action' in vk_msg:
            exported_msg['action'] = vk_msg['action']
            if 'member_id' in vk_msg['action']:
                ctx.add_user(vk_msg['action']['member_id'], self)

        if 'action_text' in vk_msg:
            exported_msg['action_text'] = vk_msg['action_text']

        if 'action_mid' in vk_msg:
            exported_msg['action_mid'] = vk_msg['action_mid']

        if self.options.arguments.save_raw:
            exported_msg['raw'] = vk_msg

        return exported_msg

    def _get_action_text(self, ctx, msg, action, action_text, action_mid):
        action_text_dict = {
            'chat_photo_update': 'Updated the chat photo',
            'chat_photo_remove': 'Removed the chat photo',
            'chat_create': 'Created the chat',
            'chat_invite_user': 'Invited user to the chat',
            'chat_kick_user': 'Kicked user from the chat',
            'chat_invite_user_by_link': 'Entered the chat by invite link'
        }

        if action == 'chat_title_update':
            return 'Changed chat title to: <span class="new-chat-title">{title}</span>'.format(title=action_text)
        elif action == 'chat_pin_message':
            return 'Pinned message <span class="new-chat-title">{text}</span>'.format(text=action_text)
        elif action == 'chat_unpin_message':
            return 'Unpinned message <span class="new-chat-title">{text}</span>'.format(text=action_text)
        elif action == 'chat_kick_user':
            if action_mid is None:
                return 'Kicked user'
            elif action_mid == msg['sender']['id']:
                return 'Left the chat'
            elif action_mid in ctx.input_json['users']:
                return 'Kicked user <span class="new-chat-title">{name}</span>'.format(name=ctx.get_user(action_mid)['name'])
            else:
                return 'Kicked user id {user_id}'.format(user_id=action_mid)
        else:
            return action_text_dict.get(action, '')

    def _to_html_action_message(self, ctx, msg):
        ctx.prev_merge_sender = None

        sender = ctx.get_user(msg['sender']['id'])

        attach_block = ''
        if 'attachments' in msg:
            attach_block = Attachment.attachments_to_html(ctx, msg['attachments'], [self.progress, self.id, self.options])

        return '''
        <div class="msg msg--level-{level} msg--action msg-action" data-json='{json}'>
            <span class="msg-action__sender">{sender_fullname}</span>
            :
            {message}
            {attach_block}
        </div>
        '''.format(**{
            'level': ctx.level,
            'json': json.dumps(msg, ensure_ascii=False) if self.options.arguments.save_json_in_html else '',
            'sender_profile': sender['link'],
            'sender_fullname': sender['name'],
            'sender_firstname': sender['first_name'],
            'sender_photo': sender['filename'],
            'date': fmt_timestamp(msg['date']),
            'message': self._get_action_text(ctx, msg, msg['action'], msg.get('action_text', ''), msg.get('action_mid', None)),
            'attach_block': attach_block
        })

    def to_html(self, ctx, msg):
        if 'action' in msg:
            return self._to_html_action_message(ctx, msg)

        extra_classes = []

        if msg['is_important']:
            extra_classes.append('msg--important')

        if msg['is_updated']:
            extra_classes.append('msg--edited')

        sender_id = msg['sender']['id']
        sender = ctx.get_user(sender_id)

        # Forward block
        fwd_block = ''
        if 'forwarded' in msg:
            nested_context = ctx.next_level()
            for fwd_msg in msg['forwarded']:
                fwd_block += self.to_html(nested_context, fwd_msg)

        if len(fwd_block) > 0:
            fwd_block = '<div class="msg-forwarded">{fwd_block}</div>'.format(fwd_block=fwd_block)

        # Attachments block
        attach_block = ''
        if 'attachments' in msg:
            attach_block += Attachment.attachments_to_html(ctx, msg['attachments'], [self.progress, self.id, self.options])

        if len(attach_block) > 0:
            attach_block = '<div class="msg-attachments">{attach_block}</div>'.format(attach_block=attach_block)

        extra_head_classes = []

        msg_date = msg['date']
        is_merged = False
        merge_date_diff = 0
        if sender_id == ctx.prev_merge_sender and msg_date - ctx.prev_merge_msg_timestamp < MSG_MERGE_TIMEOUT:
            extra_classes.append('msg--merged')
            extra_head_classes.append('msg-head--merged')
            is_merged = True
            merge_date_diff = msg_date - ctx.prev_merge_msg_timestamp

        # do not allow the next message to be merged if we have forwarded messages
        if not fwd_block:
            ctx.prev_merge_sender = sender_id
            ctx.prev_merge_msg_timestamp = msg_date

        return '''
        <div class="msg msg--level-{level} {extra_classes}" data-json='{json}'>
            <div class="msg-head {extra_head_classes}">
                <div class="msg-head__photo-block">
                    <img class="msg-head__photo" src="{sender_photo}" />
                </div>
                <div class="msg-head__info">
                    <a class="msg-head__profile" href="{sender_profile}" title="{sender_fullname}">{sender_firstname}</a>
                    <div class="msg-head__date-block">
                        <span class="msg-head__date">{date}</span>
                    </div>
                </div>
            </div>
            <div class="msg-body">
                <div class="msg-text">
                    {message}
                    {edited_block}
                </div>
                {fwd_block}
                {attach_block}
            </div>
        </div>
        '''.format(**{
            'level': ctx.level,
            'extra_classes': ' '.join(extra_classes) if extra_classes is not None else '',
            'extra_head_classes': ' '.join(extra_head_classes) if extra_head_classes is not None else '',
            'sender_profile': sender['link'],
            'sender_fullname': sender['name'],
            'sender_firstname': sender['first_name'],
            'sender_photo': sender['filename'],
            'date': fmt_timestamp(msg['date']) if not is_merged else fmt_date_diff(merge_date_diff, add_sign=True),
            'edited_block': '<span class="msg-edited">(Edited {diff} after)</span>'.format(
                diff=fmt_date_diff(msg['updated_at'] - msg_date)
            ) if msg['is_updated'] else '',
            'message': msg['message'],
            'fwd_block': fwd_block,
            'attach_block': attach_block,
            'json': json.dumps(msg, ensure_ascii=False) if self.options.arguments.save_json_in_html else ''
        })

