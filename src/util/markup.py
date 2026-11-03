
from typing import Optional


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

  @classmethod
  def markup_row(cls, band: Optional[int]) -> str:
    if band is None:
      return cls.PENDING_RANK
    if not str(band).isdigit():
      return cls.PENDING_RANK
    band = int(band)
    band = ((band-1) // 10 + 1) * 10
    if band in cls.RANK_RANGE_COLORS:
      return cls.RANK_RANGE_COLORS[band]
    return cls.UNRANKED_COLOR