#!/usr/bin/env python3

import json


class Result:
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


class Vote:
  votes = dict()
  by_name = dict()
  def __init__(self, position, name):
    self.position = int(position)
    self.name = name
    self.votes[self.position] = self
    self.by_name[name] = self


class Markup:
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
  def vote_position(cls, position, rank, game_name):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    if rank:
      result = f'{rank:>3}'
    else:
      result = '  ?'
      game_name = ''.join([ '?' ] * len(game_name))
    rank_result = f'[b]#{position:>2} ({result})[/b]'
    return f'{leader}{rank_result}  {game_name.ljust(72 - len(rank_result))}{trailer}'

  @classmethod
  def owned_list(cls, rank, game_name):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = item.ljust(61)
    if len(name_format) > 61:
      name_format = name_format[:58] + '...'
    return f'║ {leader}#[b]{n:>3}[/b]  {name_format}{trailer} ║\n'

  @classmethod
  def wishlist(cls, rank, game_name, wishlist_priority):
    leader = cls.row_leader(rank)
    trailer = cls.row_trailer(rank)
    name_format = game_name.ljust(58)
    if len(name_format) > 58:
      name_format = name_format[:55] + '...'
    return f'║ {leader}#[b]{n:>3}[/b]  {name_format}({wishlist_priority}){trailer} ║\n'

  @classmethod
  def row_leader(cls, rank):
    bgcolor = cls.bg_color(rank)
    fgcolor = cls.text_color(bgcolor)
    return f'[bgcolor={bgcolor}][color={fgcolor}]'

  @classmethod
  def row_trailer(cls, rank):
    return f'[/color][/bgcolor]'

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

with open('data.json') as f:
  data_raw = json.load(f)

for rank, result in data_raw['top200'].items():
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
  Result(**result)

for position, game in data_raw['votes'].items():
  Vote(position, game['name'])
  if game['name'] in Result.by_name:
    Result.by_name[game['name']].vote(position)

output = """[c]
╔═════════════════════════════════════════════════════════════════════╗
║                       PILLBOX'S GAME STATISTICS                     ║
╠═════════╤═══════════╤═══════════╤═══════════╤═══════════╤═══════════╣
"""

for n in range(200, 1, -10):
  if n not in Result.ranks:
    continue
  lo = n - 9
  range_label = f'{n:>3}-{lo:>3}'
  own_count = Result.count_owned(lo, n)
  sold_count = Result.count_sold(lo, n)
  want_count = Result.count_want(lo, n)
  played_count = Result.count_played(lo, n)
  voted_count = Result.count_voted(lo, n)

  row_markup_leader = Markup.row_leader(n)
  range_markup = f'[b]{range_label}[/b]'
  own_markup = Markup.own(own_count)
  sold_markup = Markup.sold(sold_count)
  want_markup = Markup.want(want_count)
  played_markup = Markup.played(played_count)
  voted_markup = Markup.voted(voted_count)
  row_markup_trailer = Markup.row_trailer(n)

  if n < 200 and n % 50 == 0:
    output += '╠═════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╣\n'
  output += f'║ {row_markup_leader}{range_markup} │ {own_markup} ┊ {sold_markup} ┊ {want_markup} ┊ {played_markup} ┊ {voted_markup}{row_markup_trailer} ║\n'

output += '╠═════════╧═══════════╧═══════════╧═══════════╧═══════════╧═══════════╣\n'

for v in range(1, 21):
  v_game = Vote.votes[v]
  if v_game.name in Result.by_name:
    rank = Result.by_name[v_game.name].rank
  else:
    rank = None
  markup = Markup.vote_position(v, rank, v_game.name)
  output += f'║ {markup} ║\n'

output += '╠═════════════════════════════════════════════════════════════════════╣\n'

own_count = Result.count_owned()
output += f'║                                                  OWN [b]{own_count:>3} / 200[/b]      ║\n'

for n in range(200, 0, -1):
  if n not in Result.ranks:
    continue
  result = Result.ranks[n]
  if result.is_owned:
    for item in result.items:
      output += Markup.owned_list(n, item)

output += '╠═════════════════════════════════════════════════════════════════════╣\n'

wish_count = Result.count_want()
output += f'║                                             WISHLIST [b]{wish_count:>3} / 200[/b]      ║\n'

for n in range(200, 0, -1):
  if n not in Result.ranks:
    continue
  result = Result.ranks[n]
  if result.wishlist_priority.lower() != "no":
    wish_markup = 'M'
    if result.wishlist_priority.lower() == 'high':
      wish_markup = 'H'
    if result.wishlist_priority.lower() == 'low':
      wish_markup = 'L'
    output += Markup.wishlist(n, result.name, wish_markup)

output += '╚═════════════════════════════════════════════════════════════════════╝\n'
output += '[/c]\n'

print(output)
