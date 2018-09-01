import json
from data.item.Data import Data
from .ObjectFetcher import ObjectFetcher


class Like(Data):
    def __init__(self, user_id, progress, dlg_id,  options):
        super().__init__(progress, dlg_id, options)
        self.user_id = user_id

    def to_json(self, ctx):
        ctx.add_user(self.user_id, self)

        return {
            'type': __class__.__name__.lower(),
            'sender': {
                'id': self.user_id
            }
        }

    def to_html(self, ctx, like_info):
        sender_id = like_info['sender']['id']
        sender = ctx.get_user(sender_id)

        return '''
            <div class="like" data-json='{json}'>
                <div class="like-head__photo-block">
                    <img class="like-head__photo" src="{sender_photo}" />
                </div>
                <div class="like-head__info">
                    <a class="like-head__profile" href="{sender_profile}" title="{sender_fullname}">{sender_firstname}</a>
                </div>
            </div>
            '''.format(**{
                'sender_profile': sender['link'],
                'sender_fullname': sender['name'],
                'sender_firstname': sender['first_name'],
                'sender_photo': sender['filename'],
                'json': json.dumps(like_info, ensure_ascii=False) if self.options.arguments.save_json_in_html else ''
            })


class FetchLikes(ObjectFetcher):
    def __init__(self, api, vk_id, item_type, item_id, options):
        super().__init__(api, vk_id, options)
        self.item_type = item_type
        self.item_id = item_id

    def _getArrayApiCall(self, offset, count):
        return self.api.call('wall.getLikes', [
                ('offset', offset),
                ('count', count),
                ('type', self.item_type),
                ('owner_id', self.id),
                ('item_id', self.item_id),
                ('rev', 1)
            ])

    def _create_object(self, item_data, progress, user_id, options):
        return Like(item_data, progress, user_id, options)

    def _html_frame(self, options):
        return '''
            <div class="likes">
            {data}
            </div>
            '''