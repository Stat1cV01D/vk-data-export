import json


class JSONSerializer:
    def __init__(self, api, options):
        self.api = api
        self.options = options

    @property
    def extension(self):
        return "json"

    def serialize(self, data_container, progress):
        json_input = ""
        for obj in data_container.get_data(progress):
            json_input += obj.to_json(progress)

        return {
            'text': json.dumps(json_input, ensure_ascii=False, indent=2)
        }

