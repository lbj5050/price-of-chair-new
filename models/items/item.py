from dataclasses import dataclass, field
from typing import Dict
import uuid
from bs4 import BeautifulSoup
import requests
import re
from models.model import Model
from common.database import Database
import models.items.constants as ItemConstants
from models.stores.store import Store


@dataclass(eq=False)
class Item(Model):
    collection: str = field(init=False, default=ItemConstants.COLLECTION)
    name: str
    url: str
    price: float = None
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)
    tag_name: str = field(init=False)
    query: Dict = field(init=False)

    def __post_init__(self, name, url, price, _id):
        store = Store.find_by_url(url)
        self.tag_name = store.tag_name
        self.query = store.query

    def load_price(self):
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()

        pattern = re.compile("(\d+.\d+)")
        match = pattern.search(string_price)
        self.price = float(match.group())

        return self.price

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url": self.url,
            "price": self.price,
        }