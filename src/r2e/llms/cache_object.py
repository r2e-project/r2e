import os
import json
from diskcache import Cache as DiskCache

from r2e.paths import CACHE_PATH, CACHE_DIR


class Cache:
    def __init__(self) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.cache_dict = DiskCache(CACHE_DIR)

    @staticmethod
    def process_payload(payload):
        if isinstance(payload, (list, dict)):
            return json.dumps(payload)
        return payload

    def get_from_cache(self, payload):
        payload_cache = self.process_payload(payload)
        if self.cache_dict.get(payload_cache):
            return self.cache_dict[payload_cache]
        return None

    def add_to_cache(self, payload, output):
        payload_cache = self.process_payload(payload)
        self.cache_dict.set(payload_cache, output)

    def save_cache(self):
        pass
