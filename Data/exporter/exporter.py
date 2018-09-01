class ExportContext:
    def __init__(self, user_fetcher, depth=0, users=None):
        self.depth = depth
        self.user_fetcher = user_fetcher
        self.users = users if users is not None else dict()

    def add_user(self, user_id, exporter=None):
        if user_id and user_id not in self.users:
            self.users[user_id] = self.user_fetcher.get_data(user_id, exporter)

    def next_level(self):
        return ExportContext(self.user_fetcher, self.depth, self.users)


class UserFetcher:
    def __init__(self, api):
        self.api = api
        self.cache = dict()

    def get_data(self, user_id, exporter=None):
        if not (user_id in self.cache):
            if user_id < 0:
                groups = self.api.call("groups.getById", [("group_id", str(-user_id))])
                data = groups[0]

                downloaded = None
                if exporter is not None:
                    downloaded = exporter.download_image(data)

                self.cache[user_id] = {
                    'name': data['name'],
                    'first_name': data['name'],
                    'last_name': '',
                    'link': 'https://vk.com/%s' % data['screen_name'],
                    'filename': downloaded
                }
            else:
                users = self.api.call("users.get", [("user_ids", str(user_id)), ("fields", "photo_50")])
                data = users[0]

                downloaded = None
                if exporter is not None:
                    downloaded = exporter.download_image(data)

                self.cache[user_id] = {
                    'name': '%s %s' % (data['first_name'], data['last_name']),
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'link': 'https://vk.com/id%s' % data['id'],
                    'filename': downloaded
                }
        return self.cache[user_id]


class Serializer(object):
    @property
    def extension(self):
        return "(no extension)"

    def serialize(self, data_container, progress):
        pass
