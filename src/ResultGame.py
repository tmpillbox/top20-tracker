from typing import Dict, List, Optional, Union


class ResultGame:
    def __init__(self, name: str, own: bool = False, wishlist: str = "no", played: bool = False, prev_owned: bool = False, owned_items: Optional[List] = None) -> None:
        self.name = str(name)
        self.own = bool(own)
        self.wishlist = str(wishlist)
        self.played = bool(played)
        self.prev_owned = bool(prev_owned)
        self.owned_items = list()
        if owned_items is not None and owned_items:
            for item in owned_items:
                if item not in self.owned_items:
                    self.owned_items.append(str(item))
        if self.own and not self.owned_items:
            self.owned_items.append(name)

    def update_values(
        self,
        own: Optional[bool] = None,
        wishlist: Optional[str] = None,
        played: Optional[bool] = None,
        prev_owned: Optional[bool] = None,
        add_owned_items: Optional[List[str]] = None,
        del_owned_items: Optional[List[str]] = None
    ) -> None:
        if own is not None:
            self.own = bool(own)
        if wishlist is not None:
            self.wishlist = str(wishlist)
        if played is not None:
            self.played = bool(played)
        if prev_owned is not None:
            self.prev_owned = bool(prev_owned)
        if add_owned_items is not None and add_owned_items:
            for item in add_owned_items:
                if item not in self.owned_items:
                    self.owned_items.append(str(item))
        if del_owned_items is not None and del_owned_items:
            for item in del_owned_items:
                if item in self.owned_items:
                    self.owned_items.remove(item)

    @property
    def as_dict(self) -> Dict[str,Union[str,bool,List[str]]]:
        obj = {
            "name": self.name,
            "own": self.own,
            "wishlist": self.wishlist,
            "played": self.played,
            "prev_owned": self.prev_owned,
            "owned": [ o for o in self.owned_items ]
        }
        return obj

    @classmethod
    def from_dict(cls, game_data: Dict) -> "ResultGame":
        game = cls(
            game_data['name'],
            own=game_data.get('own', False),
            wishlist=game_data.get('wishlist', "no"),
            played=game_data.get('played', False),
            prev_owned=game_data.get('prev_owned', False),
            owned_items=game_data.get('owned', None)
        )
        return game