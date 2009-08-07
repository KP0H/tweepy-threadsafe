# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
from threading import Thread

from . auth import BasicAuthHandler

try:
  import json
except ImportError:
  import simplejson as json

class Stream(object):

  def __init__(self, method, username, password, host='stream.twitter.com', buffer_size=1500):
    self.method = method if method[0] == '/' else '/' + method
    self.host = host
    self.auth = BasicAuthHandler(username, password)
    self.running = False
    self.buffer_size = buffer_size

  def _run(self):
    conn = httplib.HTTPConnection(self.host)
    headers = {}
    self.auth.apply_auth(None, None, headers, None)
    conn.request('POST', self.method + '.json?delimited=length', headers=headers)
    resp = conn.getresponse()
    data = ''
    while self.running:
      if resp.isclosed():
        break

      # read length
      length = ''
      while True:
        c = resp.read(1)
        if c == '\n':
          break
        length += c
      length = length.strip()
      if length.isdigit():
        length = int(length)
      else:
        continue

      # read data
      data = resp.read(length)
      jobject = json.loads(data)
      self.callback(jobject)

    conn.close()
    self.running = False

  def connect(self, callback):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.callback = callback
    self.running = True
    Thread(target=self._run).start()
    
  def disconnect(self):
    if not self.running:
      raise TweepError('Stream object not connected!')
    self.running = False
      