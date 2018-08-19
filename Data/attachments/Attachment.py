import urllib
from utils import *
from . import Unknown


class Attachment:
    def __init__(self, api, dlg_type, dlg_id, options):
        self.api = api
        self.type = dlg_type
        self.id = dlg_id
        self.attach_dir = str(self.id)
        self.output_dir = options.output_dir
        self.options = options

    def find_largest(self, obj, key_override='photo_'):
        def get_photo_keys():
            for k, v in iter(obj.items()):
                if k.startswith(key_override):
                    yield k[len(key_override):]

        return "%s%s" % (key_override, max(map(lambda k: int(k), get_photo_keys())))

    def download_file(self, url, out_filename, auto_image_ext=False, size=-1):
        if not url:
            # blocked documents or audio files go here
            return None

        abs_attach_dir = os.path.join(self.output_dir, self.attach_dir)
        if not os.path.exists(abs_attach_dir):
            os.makedirs(abs_attach_dir)
        elif not os.path.isdir(abs_attach_dir):
            raise OSError("Unable to create attachments directory %s" % abs_attach_dir)

        rel_out_path = esc("%s/%s" % (self.attach_dir, out_filename))
        abs_out_path = os.path.join(self.output_dir, rel_out_path)
        has_ext = len(os.path.splitext(rel_out_path)[1]) > 0
        if has_ext and os.path.exists(abs_out_path) and os.stat(abs_out_path).st_size > 0:
            return rel_out_path  # file was already downloaded?
        elif not has_ext and auto_image_ext:
            downloaded_image = has_downloaded_image(abs_attach_dir, out_filename)
            if downloaded_image is not None:
                return os.path.join(self.attach_dir, downloaded_image)

        def update_progress():
            display_filename = out_filename
            if auto_image_ext and not has_ext:
                display_filename = out_filename + '.jpg'  # we cannot determine it right now, but jpg is common, so...
            if size > 0:
                display_filename += ', ' + fmt_size(size)
            progress.step_msg('%s -> %s' % (url, display_filename))

        def try_download(src_url):
            nonlocal out_filename
            nonlocal rel_out_path
            nonlocal abs_out_path
            nonlocal has_ext

            try:
                request = urllib.request.urlopen(src_url, timeout=20)
                if not has_ext and auto_image_ext and 'Content-Type' in request.info():
                    ext = '.' + guess_image_ext(request.info()['Content-Type'])
                    out_filename = out_filename + ext
                    rel_out_path = rel_out_path + ext
                    abs_out_path = abs_out_path + ext
                    has_ext = True
                    update_progress()
                with open(abs_out_path, 'wb') as f:
                    f.write(request.read())
                    return True
            except Exception:
                return None

        update_progress()
        try:
            try_count = 0
            while try_count < 3:
                # sys.stdout.write("Downloading photo %s\n" % (message["id"]))
                if try_download(url):
                    return rel_out_path
                try_count += 1
        finally:
            progress.clear_step_msg()

        progress.error("Failed to retrieve file (%s) after 3 attempts, skipping\n" % url)
        return None

    def download_image(self, attachment, key_override="photo_"):
        filename = str(attachment['id'])
        url = attachment[self.find_largest(attachment, key_override)]
        return self.download_file(url, filename, True)

    @classmethod
    def get_attachment_classes(cls, attachments):
        known_types = {}
        for item in cls.__subclasses__():
            known_types[item.__name__] = item

        for att in attachments:
            if att['type'] in known_types.keys():
                obj = known_types[att['type']]()
            else:
                obj = Unknown()
            yield obj, att

    @classmethod
    def attachments_to_json(cls, context, attachments):
        results = []
        for obj, att in cls.get_attachment_classes(attachments):
            results.append(obj.to_json(context, att))

        return results

    @classmethod
    def attachments_to_html(cls, context, attachments):
        results = []
        for obj, att in cls.get_attachment_classes(attachments):
            results.append(obj.to_html(context, att))

        return results
