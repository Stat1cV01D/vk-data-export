import json
from data.item.Data import Data
from data.fetch.Comments import FetchComments
from data.fetch.Likes import FetchLikes
from data.attachments.Wall import Wall


class Post(Data):
    def __init__(self, api, vk_post, progress, dlg_id,  options):
        super().__init__(progress, dlg_id, options)
        self.vk_post = vk_post
        self.api = api
        self.comments = None
        self.likes = None

    def to_json(self, ctx):
        vk_post = self.vk_post
        exported_post = Wall(self.progress, self.id, self.options).to_json(ctx, vk_post)

        # handle comments
        if vk_post['comments']['count'] > 0:
            self.comments = FetchComments(self.api, self.id, vk_post.get('id', 0), self.options)
            exported_post['comments'] = self.comments.get_json(ctx)

        # handle likes
        if vk_post['likes']['count'] > 0:
            self.likes = FetchLikes(self.api, self.id, __class__.__name__.lower(),
                                    vk_post.get('id', 0), self.options)
            exported_post['likes'] = self.likes.get_json(ctx)

        return exported_post

    def to_html(self, ctx, post):
        wall_post = Wall(self.progress, self.id, self.options).to_html(ctx)

        # Likes block
        likes_block = ''
        if self.likes:
            likes_block = self.likes.get_html_body(ctx, self.progress)

        # Comments block
        comments_block = ''
        if self.comments:
            comments_block = self.comments.get_html_body(ctx, self.progress)

        return '''
        <div class="post post--level-{level}" data-json='{json}'>
            {wall_post}
            <div class="post-attributes">
                {likes_block}
                {comments_block}
             </div>
        </div>
        '''.format(**{
            'level': ctx.level,
            'wall_post': wall_post,
            'likes_block': likes_block,
            'comments_block': comments_block,
            'json': json.dumps(post, ensure_ascii=False) if self.options.arguments.save_json_in_html else ''
        })
