from data.item.Data import Data
from .Unknown import Unknown


class Attachment(Data):
    def __init__(self, progress, dlg_id, options):
        super().__init__(progress, dlg_id, options)

    @classmethod
    def get_attachment_classes(cls, attachments, ctr_args):
        known_types = {}
        for sub in Attachment.__subclasses__():
            known_types[sub.__name__.lower()] = sub

        for att in attachments:
            if att['type'] in known_types.keys():
                obj = known_types[att['type']](*ctr_args)
            else:
                obj = Unknown(att)
            yield obj, att

    @classmethod
    def attachments_to_json(cls, context, attachments, ctr_args):
        results = []
        for obj, att in cls.get_attachment_classes(attachments, ctr_args):
            results.append(obj.to_json(context, att[att['type']]))

        return results

    @classmethod
    def attachments_to_html(cls, context, attachments, ctr_args):
        attach_block = ''
        for obj, att in cls.get_attachment_classes(attachments, ctr_args):
            attach_block += obj.to_html(context, att)

        if len(attach_block) > 0:
            attach_block = '<div class="attachments">{attach_block}</div>'.format(attach_block=attach_block)

        return attach_block
