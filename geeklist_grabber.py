#!/usr/bin/env python3


import argparse
import json
import sys
import time

from libbgg.apiv1 import BGG

last_data = dict()

class Item:
  def __init__(self, init_data):
    self.last = init_data
    self.id = init_data['objectid']
    self.name = init_data['objectname']
    self.body = init_data['body']['TEXT']
    self.rank = int(self.body.split('[b][size=18]#')[-1].split('[/size][/b]')[0])

  @property
  def csv(self):
    return self._csv(';')

  def _csv(self, delimiter):
    return f'{self.id}{delimiter}{self.name}{delimiter}{self.rank}'

def main(geeklist_id, output_stream):
  bgg = BGG()

  geeklist = bgg.get_geeklist(geeklist_id)
  while len(geeklist) < 0 and 'geeklist' not in geeklist:
    if 'message' in geeklist:
      print(f"[BGGAPI]: {geeklist['message']}")
    else:
      print(f'[BGGAPI] is misbehaving.\n{repr(geeklist)}')
      return
    time.sleep(30)

  for item in geeklist['geeklist']['item']:
    last_data[item['objectname']] = item
    i = Item(item)
    output_stream.write(i.csv + '\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog="geeklist_grabber", description="Download a Top 200 geeklist")
  parser.add_argument('geeklist_id', type=int)
  parser.add_argument('-o', '--output-file',
                      action='store', type=argparse.FileType('w'), dest='output', default=sys.stdout,
                      help='Output to a file. Default is output to terminal')
  args = parser.parse_args()
  main(args.geeklist_id, args.output)