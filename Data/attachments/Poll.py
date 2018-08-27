from .Attachment import Attachment


class Poll(Attachment):
    def to_json(self, context, poll):
        return {
            'type': __class__.__name__.lower(),
            'question': poll.get('question', ''),
            'owner_id': poll.get('owner_id', 0),
            'date': poll.get('created', 0),
            'votes': poll.get('votes', 0),
            'answer_id': poll.get('answer_id', 0),
            'answers': poll.get('answers', []),
            'anonymous': poll.get('anonymous', 0)
        }

    def to_html(self, ctx, attach):
        return '''
        <div class="attach attach-poll">
            <span class="attach-poll__title">{description}</span>
            <div class="attach-poll__question">{question}</div>
        </div>
        '''.format(**attach)
