#!/usr/bin/env python3

import argparse
import json
from typing import Dict, Union


class GameResult:
  ranks = dict()
  by_name = dict()

  @classmethod
  def _get_ranks(cls, range_start, range_end):
    return [ r for r in cls.ranks if range_start <= r <= range_end ]
    

  @classmethod
  def owned_games(cls, range_start=1, range_end=200):
    for rank in [ r for r in cls._get_ranks(range_start, range_end) ]:
      yield cls.ranks[rank]

  @classmethod
  def wished_games(cls, range_start=1, range_end=200):
    for rank in [ r for r in cls._get_ranks(range_start, range_end) ]:
      yield cls.ranks[rank]

  @classmethod
  def count_owned(cls, range_start=1, range_end=200):
    return sum([ int(len(cls.ranks[r].items) > 0) for r in cls._get_ranks(range_start, range_end) ])

  @classmethod
  def count_sold(cls, range_start=1, range_end=200):
    return sum([ int(cls.ranks[r].prev_owned) for r in cls._get_ranks(range_start, range_end) ])

  @classmethod
  def count_want(cls, range_start=1, range_end=200):
    return sum([ int(cls.ranks[r].wishlist_priority.title() != "No") for r in cls._get_ranks(range_start, range_end) ])

  @classmethod
  def count_played(cls, range_start=1, range_end=200):
    return sum([ int(cls.ranks[r].played) for r in cls._get_ranks(range_start, range_end) ])

  @classmethod
  def count_voted(cls, range_start=1, range_end=200):
    return sum([ int(cls.ranks[r].is_voted()) for r in cls._get_ranks(range_start, range_end) ])

  def __init__(self, rank, name, is_owned, wishlist_priority, played, owned_items=None, prev_owned=False):
    self.rank = int(rank)
    self.name = name
    self.vote_position = None
    self.wishlist_priority = wishlist_priority
    self.played = played
    self.prev_owned = prev_owned
    if owned_items:
      self.is_owned = True
      self.items = [ item for item in owned_items ]
    elif is_owned:
      self.is_owned = True
      self.items = [ name ]
    else:
      self.is_owned = False
      self.items = list()
    self.ranks[self.rank] = self
    for item in self.items:
      self.by_name[item] = self

  def vote(self, position):
    print(f'CASTING VOTE FOR {self.name} @ {position}')
    self.vote_position = position

  def is_voted(self):
    return self.vote_position is not None and 1 <= int(self.vote_position) <= 20


class GameVote:
  current_year: Union[str, None] = None
  votes: Dict[int, "GameVote"] = dict()
  by_name: Dict[str, "GameVote"] = dict()

  @classmethod
  def set_current_year(cls, year: Union[int, str]) -> None:
    cls.current_year = year

  def __init__(self, name: str, votes: Dict[Union[int, str], Union[int, str]]) -> None:
    self.position = votes[self.current_year]
    self.name = name
    self.by_name[name] = self
    try:
      self.votes[int(self.position)] = self
    except:
      pass
  
  @property
  def is_top_20(self) -> bool:
    try:
      pos = int(self.position)
      return pos <= 20
    except:
      return False

class Markup:
  BLOCK_START = ''
  BLOCK_END = ''
  UNRANKED_COLOR = '#A4ACBA'
  PENDING_RANK = '#E3E3CA'

  RANK_RANGE_COLORS = {
    200: "#E5C5E5",
    190: "#D7B8DF",
    180: "#C4AAD8",
    170: "#AF9DD1",
    160: "#9790CB",
    150: "#838AC4",
    140: "#768DBC",
    130: "#6993B5",
    120: "#5D9CAE",
    110: "#50A6A6",
    100: "#4BA590",
     90: "#46A478",
     80: "#42A25E",
     70: "#3DA143",
     60: "#4C9F39",
     50: "#619E35",
     40: "#779C31",
     30: "#8E9A2D",
     20: "#97892A",
     10: "#956C26"
  }

  ALT_RANK_RANGE_COLORS = {
    200: "#FEFCEB",
    190: "#F7FEE5",
    180: "#E9FDE0",
    170: "#DBFBDE",
    160: "#D6FAE8",
    150: "#D1F8F4",
    140: "#CDE9F6",
    130: "#C9D5F3",
    120: "#CAC5F0",
    110: "#D8C1ED",
    100: "#C8B4E2",
     90: "#AAADDA",
     80: "#A0BCD2",
     70: "#96C9C5",
     60: "#8DC0A3",
     50: "#87B783",
     40: "#98AE7A",
     30: "#A5A171",
     20: "#9C7E68",
     10: "#916064"
  }

  @classmethod
  def resolve_rank_band(cls, rank):
    return (rank + 9) // 10 * 10
  
  @classmethod
  def own(cls, count):
    return f'OWN{count:>6}'

  @classmethod
  def sold(cls, count):
    return f'SOLD{count:>5}'

  @classmethod
  def want(cls, count):
    return f'WANT{count:>5}'

  @classmethod
  def played(cls, count):
    return f'PLAYED{count:>3}'

  @classmethod
  def voted(cls, count):
    return f'VOTED{count:>4}'

  @classmethod
  def bg_color(cls, rank):
    if rank is None:
      return cls.PENDING_RANK
    band = cls.resolve_rank_band(rank)
    if band in cls.RANK_RANGE_COLORS:
      return cls.RANK_RANGE_COLORS[band]
    return cls.PENDING_RANK

  @classmethod
  def text_color(cls, bgcolor):
    r, g, b = cls.hex2rgb(bgcolor)
    if r * 0.299 + g * 0.587 + b * 0.144 > 150:
      return '#000000'
    return '#ffffff'

  @staticmethod
  def hex2rgb(hex_color):
    val = hex_color.strip('#')
    lv = len(val)
    return tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

class BBCode(Markup):
  BLOCK_START = '[c]'
  BLOCK_END = '[/c]'
  @classmethod
  def vote_position(cls, position, rank, game_name):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    if rank:
      result = f'{rank:>4}'
    else:
      result = '   ?'
      game_name = ''.join([ '?' ] * len(game_name))
    rank_result = f'[b]#{position:>2} ({result})[/b]'
    return f'{leader}{rank_result}  {game_name.ljust(72 - len(rank_result))}{trailer}'

  @classmethod
  def owned_list(cls, rank, game_name):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = game_name.ljust(61)
    if len(name_format) > 61:
      name_format = name_format[:58] + '...'
    return f'║ {leader}#[b]{rank:>3}[/b]  {name_format}{trailer} ║\n'

  @classmethod
  def wishlist(cls, rank, game_name, wishlist_priority):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = game_name.ljust(58)
    if len(name_format) > 58:
      name_format = name_format[:55] + '...'
    return f'║ {leader}#[b]{rank:>3}[/b]  {name_format}({wishlist_priority}){trailer} ║\n'

  @classmethod
  def row_leader(cls, rank):
    bgcolor = cls.bg_color(rank)
    fgcolor = cls.text_color(bgcolor)
    return f'[bgcolor={bgcolor}][color={fgcolor}]'

  @classmethod
  def row_trailer(cls, rank):
    return f'[/color][/bgcolor]'

class Markdown(Markup):
  BLOCK_START = '<code>\n'
  BLOCK_END = '</code>'
  @classmethod
  def vote_position(cls, position, rank, game_name):
    raw_game_name = game_name
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    if rank:
      result = f'{rank:>3}'
    else:
      result = '  ?'
      game_name = ''.join([ '?​' ] * len(game_name))
    rank_result = f'**#{position:>2} ({result})**'
    return f'{leader}{rank_result}  {game_name.ljust(69 - len(rank_result) + len(game_name) - len(raw_game_name))}{trailer}'

  @classmethod
  def owned_list(cls, rank, game_name):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = game_name.ljust(61)
    if len(name_format) > 61:
      name_format = name_format[:60] + '...'
    return f'║ {leader}#**{rank:>3}**  {name_format}{trailer} ║\n'

  @classmethod
  def wishlist(cls, rank, game_name, wishlist_priority):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = game_name.ljust(58)
    if len(name_format) > 58:
      name_format = name_format[:57] + '...'
    return f'║ {leader}#**{rank:>3}**  {name_format}({wishlist_priority}){trailer} ║\n'

  @classmethod
  def row_leader(cls, rank):
    bgcolor = cls.bg_color(rank)
    fgcolor = cls.text_color(bgcolor)
    return f'<span style="color: {fgcolor}; background-color: {bgcolor}">'

  @classmethod
  def row_trailer(cls, rank):
    return f'</span>'


def main(args):
  if args.format == "bbcode":
    markup = BBCode
  elif args.format == "markdown":
    markup = Markdown
  else:
    print(f'WARNING: unknown format: {args.format}')
    markup = BBCode
  
  with open(args.votes) as f:
    data_raw_votes = json.load(f)

  with open(args.results) as f:
    data_raw_results = json.load(f)

  current_year = data_raw_results['year']
  GameVote.set_current_year(current_year)

  for rank, result in data_raw_results['results'].items():
    if rank == '':
      continue
    result.update( { "rank": rank } )
    result['is_owned'] = result['own']
    del result['own']
    result['wishlist_priority'] = result['wishlist']
    del result['wishlist']
    if 'owned' in result:
      result['owned_items'] = result['owned']
      del result['owned']
    GameResult(**result)

  for game_name, game_data in data_raw_votes.items():
    if 'vote_ranks' in game_data:
      game: GameVote = GameVote(game_name, game_data['vote_ranks'])
      if game_name in GameResult.by_name:
        GameResult.by_name[game_name].vote(game.position)
      elif game.is_top_20:
        print(f'# MISSING Result: {game_name}')

  output = f"""{markup.BLOCK_START}
╔═════════════════════════════════════════════════════════════════════╗
║                       PILLBOX'S GAME STATISTICS                     ║
╠═════════╤═══════════╤═══════════╤═══════════╤═══════════╤═══════════╣
"""

  for n in range(200, 1, -10):
    if n not in GameResult.ranks:
      continue
    lo = n - 9
    range_label = f'{n:>3}-{lo:>3}'
    own_count = GameResult.count_owned(lo, n)
    sold_count = GameResult.count_sold(lo, n)
    want_count = GameResult.count_want(lo, n)
    played_count = GameResult.count_played(lo, n)
    voted_count = GameResult.count_voted(lo, n)

    row_markup_leader = markup.row_leader(n)
    range_markup = f'[b]{range_label}[/b]'
    own_markup = markup.own(own_count)
    sold_markup = markup.sold(sold_count)
    want_markup = markup.want(want_count)
    played_markup = markup.played(played_count)
    voted_markup = markup.voted(voted_count)
    row_markup_trailer = markup.row_trailer(n)

    if n < 200 and n % 50 == 0:
      output += '╠═════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╣\n'
    output += f'║ {row_markup_leader}{range_markup} │ {own_markup} ┊ {sold_markup} ┊ {want_markup} ┊ {played_markup} ┊ {voted_markup}{row_markup_trailer} ║\n'

  output += '╠═════════╧═══════════╧═══════════╧═══════════╧═══════════╧═══════════╣\n'

  for v in range(1, 21):
    v_game = GameVote.votes[v]
    if v_game.name in GameResult.by_name:
      rank = GameResult.by_name[v_game.name].rank
    else:
      rank = None
    out_markup = markup.vote_position(v, rank, v_game.name)
    output += f'║ {out_markup} ║\n'

  output += '╠═════════════════════════════════════════════════════════════════════╣\n'

  own_count = GameResult.count_owned()
  output += f'║                                                  OWN [b]{own_count:>3} / 200[/b]      ║\n'

  for n in range(200, 0, -1):
    if n not in GameResult.ranks:
      continue
    result = GameResult.ranks[n]
    if result.is_owned:
      for item in result.items:
        output += markup.owned_list(n, item)

  output += '╠═════════════════════════════════════════════════════════════════════╣\n'

  wish_count = GameResult.count_want()
  output += f'║                                             WISHLIST [b]{wish_count:>3} / 200[/b]      ║\n'

  for n in range(200, 0, -1):
    if n not in GameResult.ranks:
      continue
    result = GameResult.ranks[n]
    if result.wishlist_priority.lower() != "no":
      wish_markup = 'M'
      if result.wishlist_priority.lower() == 'high':
        wish_markup = 'H'
      if result.wishlist_priority.lower() == 'low':
        wish_markup = 'L'
      output += markup.wishlist(n, result.name, wish_markup)

  output += '╚═════════════════════════════════════════════════════════════════════╝\n'
  output += f'{markup.BLOCK_END}\n'
  
  full_space = ' '
  zero_space = '​​'
  if args.format == 'markdown':
    old_output = output
    output = ''
    for c in old_output:
      if c == ' ':
        output = f'{output}{full_space}'
      else:
        output = f'{output}{c}'

  print(output)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='top20-tracker', description='Peoples Choice Top20 Results Tracker')
  parser.add_argument('--votes', nargs='?', type=str, default="votes.json")
  parser.add_argument('--results', nargs='?', type=str, default="results.json")
  parser.add_argument('--format', type=str, default="bbcode", choices=["bbcode", "markdown"])
  args = parser.parse_args()
  main(args)