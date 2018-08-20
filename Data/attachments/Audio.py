from utils import *
from .Attachment import Attachment


class Audio(Attachment):
    def to_json(self, context, audio):
        filename = '%s.mp3' % audio.get('id', 0)
        url = audio.get('url', '')

        downloaded = None
        if self.options.arguments.audio and context.depth <= self.options.arguments.audio_depth:
            if not url or "audio_api_unavailable.mp3" in url:
                self.progress.error("Audio file [%s - %s] is no more available, skipping\n"
                                    % (audio.get('artist', ''), audio.get('title', '')))
            else:
                downloaded = self.download_file(url, filename)

        return {
            'type': __class__.__name__.lower(),
            'artist': audio.get('artist', ''),
            'title': audio.get('title', ''),
            'duration': audio.get('duration', 0),
            'filename': downloaded,
            'url': url
        }

    def to_html(self, ctx, attach):
        args = {**attach, **{'duration': fmt_time(attach['duration'])}}

        if 'downloaded' in attach and attach['downloaded'] is not None:
            audio_block = '<audio class="attach-audio__audio" controls src="{filename}" />'.format(**attach)
        else:
            audio_block = '<div class="attach-audio__audio attach-audio__audio--failed">Unavailable</div>'

        return '''
        <div class="attach attach-audio">
            <div class="attach-audio__title">
                Audio:
                <span class="attach-audio__author">
                    <span class="attach-audio__composition-artist">{artist}</span>
                    -
                    <span class="attach-audio__composition-title">{title}</span>
                </span>
            </div>
            <span class="attach-audio__audio-block">
                {audio_block}
                <div class="attach-audio__duration">{duration}</div>
            </span>
        </div>
        '''.format(**args, audio_block=audio_block)
