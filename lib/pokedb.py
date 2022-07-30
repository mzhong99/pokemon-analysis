import requests
import urllib.parse
import os
import json

class PokeDB:
    NODE_FILE_NAME = "data.json"

    def __init__(self, cache_dir: str, api_link: str):
        self._base_cache_dir = os.path.expanduser(cache_dir)
        self._api_link = api_link

        os.makedirs(self._base_cache_dir, exist_ok=True)

    def _get_from_cache(self, endpoint: str):
        cached_path = os.path.join(self._base_cache_dir, endpoint, PokeDB.NODE_FILE_NAME)
        if not os.path.isfile(cached_path):
            return None
        with open(cached_path, "r") as rawfile:
            return json.load(rawfile)
        
    def _get_from_endpoint(self, endpoint: str, **params):
        raw_url = urllib.parse.urljoin(self._api_link, endpoint)
        req = requests.models.PreparedRequest()
        req.prepare_url(raw_url, params)

        response = requests.get(req.url)
        response.raise_for_status()

        cached_path = os.path.join(self._base_cache_dir, endpoint, PokeDB.NODE_FILE_NAME)
        os.makedirs(os.path.dirname(cached_path), exist_ok=True)
        with open(cached_path, "w") as rawfile:
            rawfile.write(response.text)

        response_dict = json.loads(response.text)
        if "count" in response_dict.keys() and not params:
            return self._get_from_endpoint(endpoint, offset=0, limit=response_dict["count"])
        return response_dict
    
    def __getitem__(self, endpoint: str):
        response = self._get_from_cache(endpoint)
        if response != None:
            return response
        return self._get_from_endpoint(endpoint)
