# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import sys
import urllib
import urllib2
import os
import cgi
import argparse
import vk_auth
import ConfigParser


parser = argparse.ArgumentParser(description="Exports VK.COM messages into HTML files. "
                                             "Login and password should be specified in config.ini file")
parser.add_argument('--person', type=int, dest="person", help="ID of person whose dialog you want to export")
parser.add_argument('--chat', type=int, dest="chat", help="ID of group chat which you want to export")
parser.add_argument('--group', type=int, dest="group", help="ID of public group whose dialog you want to export")


config = ConfigParser.ConfigParser()
config.read('config.ini')


class VkApi:
  token = None
  user_id = None
  login = config.get('auth', 'login')
  password = config.get('auth', 'password')
  app_id = config.get('auth', 'appid')

  def initialize(self):
    try:
      self.token, self.user_id = vk_auth.auth(self.login, self.password, self.app_id, 'messages')
      # self.call('stats.trackVisitor', [])
    except RuntimeError:
      sys.stdout.write("Authentication failed, maybe login/password are wrong?\n")

    sys.stdout.write("Authentication successful\n")

  def call(self, method, params):
    params.append(("access_token", self.token))
    params.append(("v", "5.52"))
    url = "https://api.vk.com/method/%s?%s" % (method, urllib.urlencode(params))

    for j in range(3):
      try:
        return json.loads(urllib2.urlopen(url, timeout=20).read())["response"]
      except Exception as e:
        sys.stdout.write('Got error while requesting api method %s, trying to resume...\n' % method)

    raise RuntimeError('Failed to call the API\n')


def fmt_time(secs):
  return str(datetime.timedelta(seconds=secs))


def esc(str):
  return cgi.escape(str)


class Progress:
  total_stages = 0
  cur_stage = 0
  steps_on_this_stage = 0

  def next_stage(self):
    if self.steps_on_this_stage != 0:
      self.update(self.steps_on_this_stage, self.steps_on_this_stage)
    sys.stdout.write('\n')
    sys.stdout.flush()
    self.cur_stage += 1

  def update(self, steps, total_steps):
    self.steps_on_this_stage = total_steps
    percent = (float(steps) / float(total_steps)) * 100
    title = '%s of %s' % (self.cur_stage + 1, self.total_stages)
    text = title.ljust(10) + ' [' + ('#' * (int(5 * round(float(percent) / 5)) / 5)).ljust(20) + ']'
    sys.stdout.write('\r' + text)
    sys.stdout.flush()


progress = Progress()


def fetch_all_dialogs(api):
  offset = 0
  while True:
    dialogs = api.call("messages.getDialogs", [("offset", offset), ("count", 200)])
    if len(dialogs['items']) == 0:
      return
    for dialog in dialogs['items']:
      yield dialog
    offset += len(dialogs['items'])


arguments = parser.parse_args()

api = VkApi()
api.initialize()


class UserFetcher:
  api = None
  cache = {}

  def __init__(self, api):
    self.api = api

  def get_data(self, user_id):
    if not (user_id in self.cache):
      self.cache[user_id] = self.api.call("users.get", [("user_ids", str(user_id))])[0]
    return self.cache[user_id]


users = UserFetcher(api)


class AttachContext:
  prefix = ''

  def __init__(self, prefix):
    self.prefix = prefix


class DialogExporter:
  api = None
  type = None
  id = None
  attach_dir = ''
  out_obj = None

  def __init__(self, api, type, id):
    self.api = api
    self.type = type
    self.id = id
    self.attach_dir = str(self.id)

  @property
  def out(self):
    if self.out_obj == None:
      self.out_obj = codecs.open(
       'vk_export_%s_%s.html' % (self.type, self.id),
       "w+", "utf-8"
      )
    return self.out_obj

  def find_largest(self, obj, key_override='photo_'):
    def get_photo_keys():
      for k, v in obj.iteritems():
        if k.startswith(key_override):
          yield k[len(key_override):]

    return "%s%s" % (key_override, max(map(lambda k: int(k), get_photo_keys())))

  def download_image(self, message, key_override="photo_"):
    if not os.path.exists(self.attach_dir):
      os.makedirs(self.attach_dir)
    elif not os.path.isdir(self.attach_dir):
      raise OSError("Unable to create attachments directory %s" % self.attach_dir)

    output_filename = esc("%s/%d.jpg" % (self.attach_dir, message["id"]))
    if os.path.exists(output_filename) and os.stat(output_filename).st_size > 0:
      return output_filename  # image was already downloaded?

    def try_download(src_url):
      try:
        request = urllib2.urlopen(src_url, timeout=20)
        with open(output_filename, 'wb') as f:
          f.write(request.read())
          return True
      except Exception as e:
        return None

    src_url = message[self.find_largest(message, key_override)]
    try_count = 0
    while try_count < 3:
      # sys.stdout.write("Downloading photo %s\n" % (message["id"]))
      if try_download(src_url):
        return output_filename
      try_count += 1

    sys.stdout.write("Failed to retrieve image (%s) after 3 attempts, skipping\n" % src_url)
    return None

  def fetch_messages(self):
    offset = 0

    selector = 'user_id' if self.type == 'user' else 'peer_id'
    id = self.id if self.type == 'user' else (2000000000 + self.id if self.type == 'chat' else -self.id)

    while True:
      messages = self.api.call('messages.getHistory', [('offset', offset), ('count', 200), (selector, id), ('rev', 1)])
      if len(messages['items']) == 0:
        break
      for msg in messages['items']:
        yield (msg, messages['count'])
      offset += len(messages['items'])

  def handle_link(self, context, link):
    self.out.write(u'<div class="att att--link"><span class="att__title">%sLink: </span><a href="%s" title="%s">%s</a></div>' % (
      context.prefix,
      esc(link['url']),
      esc(link['description']),
      esc(link['title'])
    ))

  def handle_photo(self, context, photo):
    downloaded = self.download_image(photo)
    if downloaded != None:
      self.out.write(u"""<div class="att att--photo"><span class="att__title">%sPhoto: </span><img src="%s" data-original="%s"
                         alt="%s" title="%s"/></div>""" % (
                context.prefix,
                downloaded,
                esc(self.find_largest(photo)),
                esc(photo['text']),
                esc(photo['text'])))
    else:
      self.out.write(u'<div class="att att--photo att--failed"><span class="att__title">%sPhoto: </span><a href="%s">%s</a></div>' % (
                context.prefix,
                esc(self.find_largest(photo)),
                esc(photo['text'])))

  def handle_sticker(self, context, sticker):
    downloaded = self.download_image(sticker)
    if downloaded != None:
      self.out.write(u"""<div class="att att--sticker"><span class="att__title">%sSticker: </span><img src="%s"
                     data-original="%s"/></div>""" % (
        context.prefix,
        downloaded,
        esc(self.find_largest(sticker))))
    else:
      self.out.write(
        u'<div class="att att--sticker att--failed"><span class="att__title">%sSticker: </span>[Failed to download sticker %s]</div>' % (
          context.prefix,
          esc(self.find_largest(sticker))))

  def handle_video(self, context, video):
    video_thumb = self.download_image(video)

    self.out.write(u"""<div class="att att--video" title="%s"><span class="att__title">%sVideo: </span><a href="%s">%s
                    [Duration: %s, Views: %s]</a> <div class="att__thumb"><img src="%s" /></div></div>""" % (
                esc(video["description"]),
                context.prefix,
                esc("https://vk.com/video%s_%s" % (video['owner_id'], video['id'])),
                esc(video["title"]),
                fmt_time(video["duration"]),
                video['views'],
                video_thumb if video_thumb != None else ''))

  def handle_wall(self, context, wall):
    self.out.write(u'<div class="att att--wall"><span class="att__title">%s:Wall post <a href="%s">[%s, on %s]</a>: </span>%s' % (
                context.prefix,
                "https://vk.com/wall%s_%s" % (wall['from_id'], wall['id']),
                wall["from_id"],
                wall["date"],
                esc(wall["text"])))

    if "attachments" in wall:
      self.export_attachments(AttachContext(context.prefix + '>'), wall['attachments'])

    self.out.write(u'</div>')

  def handle_audio(self, context, audio):
    self.out.write(u'<div class="att att--audio"><span class="att__title">%sAudio: </span><strong>%s</strong> - %s [%s]</div>' % (
              context.prefix,
              esc(audio["artist"]),
              esc(audio["title"]),
              fmt_time(audio["duration"])))

  def handle_doc(self, context, doc):
    self.out.write(u'<div class="att att--doc"><span class="att__title">%sDocument: </span>%s</div>' % (
              context.prefix,
              esc(doc["title"])))

  def handle_gift(self, context, gift):
    gift_thumb = self.download_image(gift, 'thumb_')

    self.out.write('<div class="att att--gift"><span class="att__title">%sGift: </span><img src="%s"/></div>' % (
      context.prefix,
      gift_thumb if gift_thumb != None else ''
    ))

  def handle_unknown(self, context, attachment):
    self.out.write('<div class="att att--unknown"><span class="att__title">%sUnknown: </span>Unknown attachment with type "%s"</div>' % (
      context.prefix,
      esc(attachment['type'])
    ))

  def export_attachments(self, context, attachments):
    known_types = ('photo', 'video', 'audio', 'doc', 'wall', 'sticker', 'link', 'gift')

    for att in attachments:
      if att['type'] in known_types:
        getattr(self, 'handle_' + att['type'])(context, att[att['type']])
      else:
        self.handle_unknown(context, att)

  def export(self):
    self.out.write('<!DOCTYPE html><head><meta charset="utf-8"/><style>%s</style></head><body>' % embed_css)

    cur_step = 0

    for msg, total in self.fetch_messages():
      if cur_step == 0:
        progress.update(0, total)

      # write message head
      from_id = msg['from_id']

      self.out.write(u'''<div class="msg"><div class="msg-head">[{date}] <a href="{profile}" title="{full_name}">
                      {first_name}</a>:</div><div class="msg-body">{message}</div>'''.format(**{
                'date': datetime.datetime.fromtimestamp(
                    int(msg["date"])).strftime('%Y-%m-%d %H:%M:%S'),

                'full_name': esc('%s %s' % (
                    users.get_data(from_id)['first_name'], users.get_data(from_id)['last_name'])),

                'first_name': esc(users.get_data(from_id)['first_name']),

                'profile': 'https://vk.com/id%s' % from_id,

                'message': esc(msg["body"])
      }))

      # now write attachments
      if 'attachments' in msg:
        self.export_attachments(AttachContext('+'), msg['attachments'])

      # and now write footer
      self.out.write(u'</div>')

      cur_step += 1
      if cur_step % 50 == 0:
        progress.update(cur_step, total)

    self.out.write('</body>')


# read css file to embed into generated html
embed_css = ''
try:
  with open('style.css', 'r') as css_file:
    embed_css = css_file.read()
except Exception as err:
  sys.stdout.write('Failed to read style.css file: %s \n' % str(err))

exps = []

if arguments.person != None:
  exps = [DialogExporter(api, 'user', arguments.person)]
elif arguments.chat != None:
  exps = [DialogExporter(api, 'chat', arguments.chat)]
elif arguments.group != None:
  exps = [DialogExporter(api, 'group', arguments.group)]
else:
  for dialog in fetch_all_dialogs(api):
    exporter = None

    last_msg = dialog['message']

    if 'chat_id' in last_msg:
      # this is group chat
      exporter = DialogExporter(api, 'chat', last_msg['chat_id'])
    else:
      exporter = DialogExporter(api, 'user', last_msg['user_id'])

    exps.append(exporter)

sys.stdout.write('Exporting %d dialogs\n' % len(exps))
progress.total_stages = len(exps)
for exp in exps:
  exp.export()
  progress.next_stage()
