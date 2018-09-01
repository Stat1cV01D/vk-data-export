from .ObjectFetcher import ObjectFetcher
from data.item.Post import Post


class FetchPosts(ObjectFetcher):
    def __init__(self, api, options):
        super().__init__(api, api.user_id, options)

    def _getArrayApiCall(self, offset, count):
        return self.api.call('wall.get', [
                ('offset', offset),
                ('count', count),
                ('user_id', self.id)
            ])

    def _create_object(self, item_data, progress, vk_id, options):
        return Post(item_data, progress, vk_id, options)

    def _html_frame(self, options):
        return '''
            <div class="wall">
            {data}
            </div>
            '''

