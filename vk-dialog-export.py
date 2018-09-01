# -*- coding: utf-8 -*-
from api import *
from options import *
from data.exporter.html_serializer import *
from data.exporter.json_serializer import *
from progress import *

# Needed for __subclasses__() to work

from data.fetch.Posts import FetchPosts
from data.fetch.Conversations import FetchConversations


api = VkApi()
if not api.initialize():
    sys.exit(-1)


options = Options()
progress = Progress()


exporters = []

if options.arguments.export_dialog is not None:
    sys.stdout.write('Exporting dialogs...\n')
    exporters.append(FetchConversations(api, options))
if options.arguments.export_wall is not None:
    sys.stdout.write('Exporting wall posts...\n')
    exporters.append(FetchPosts(api, options))

if not options.arguments.docs:
    sys.stdout.write('Attached documents are not downloaded by default. Restart the script with --docs to enable downloading documents\n')

progress.total_stages = len(exporters)
for exp in exporters:
    serializer = None
    if options.output_format == 'json':
        serializer = JSONSerializer(api, options)
    elif options.output_format == 'html':
        serializer = HTMLSerializer(api, options)
    else:
        raise RuntimeError("Unknown format")

    exported_data = serializer.serialize(exp, progress)
    with codecs.open(os.path.join(options.output_dir, str(exp.id) + "." + serializer.extension), "w", encoding="utf-8") as f:
        f.write(exported_data['text'])

    if 'files' in exported_data:
        for filename, content in exported_data['files'].items():
            with codecs.open(os.path.join(options.output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)

    progress.next_stage()
