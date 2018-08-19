from utils import *
from . import Attachment


class Voice(Attachment):
    def to_json(self, context, audio_msg):
        filename = '%s.%s' %(audio_msg.get('id', 0), audio_msg.get('ext', 'mp3'))
        msg_preview = audio_msg.get('preview', {}).get('audio_msg', {})
        url = msg_preview.get('link_mp3') or msg_preview.get('link_ogg') or ''

        downloaded = None
        if not self.options.arguments.no_voice:
            if url:
                downloaded = self.download_file(url, filename)
            else:
                progress.error("Voice message is no more available, skipping\n")

        return {
            'type': self.__name__,
            'filename': downloaded,
            'url': url,
            'duration': msg_preview.get('duration', 0),
            'id': audio_msg.get('id', 0),
            'owner_id': audio_msg.get('owner_id', 0),
            'date': audio_msg.get('date', 0)
        }

    def to_html(self, ctx, attach):
        args = {**attach, **{'duration': fmt_time(attach['duration'])}}

        return '''
        <div class="attach attach-voice">
            <div class="attach-voice__title">Voice message</div>
            <div class="attach-voice__audio-block">
                <audio class="attach-voice__audio" controls src="{filename}"></audio>
                <div class="attach-voice__duration">{duration}</div>
            </div>
        </div>
        '''.format(**args)
