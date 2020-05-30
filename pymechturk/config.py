import csv
import json
from typing import Dict
from dataclasses import dataclass, field


@dataclass(init=False, frozen=True)
class Environment(object):
    endpoint: str
    preview: str


@dataclass(init=False, frozen=True)
class Production(Environment):
    endpoint: str = "https://mturk-requester.us-east-1.amazonaws.com"
    preview: str = "https://www.mturk.com/mturk/preview"


@dataclass(init=False, frozen=True)
class Sandbox(Environment):
    endpoint = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
    preview = "https://workersandbox.mturk.com/mturk/preview"


@dataclass
class AmazonIAMUser(object):
    def __init__(self):
        self.user_name: str = field(default_factory=str)
        self.password: str = field(default_factory=str)
        self.access_key_id: str = field(default_factory=str)
        self.secret_access_key: str = field(default_factory=str)
        self.console_login_link: str = field(default_factory=str)

    def from_file(self, file_path: str) -> "AmazonIAMUser":
        extension = file_path.split('.')[-1]
        if extension == "csv":
            credentials = self._load_csv(file_path)
        elif extension == "json":
            credentials = self._load_json(file_path)
        else:
            raise Exception("Unknown file extension")
        self._update_fields(credentials)
        return self

    def _update_fields(self, credentials: Dict[str, str]):
        self.user_name: str = credentials["User name"]
        self.password: str = credentials["Password"]
        self.access_key_id: str = credentials["Access key ID"]
        self.secret_access_key: str = credentials["Secret access key"]
        self.console_login_link: str = credentials["Console login link"]

    @staticmethod
    def _load_csv(path: str) -> dict:
        with open(path, 'r') as file:
            return next(csv.DictReader(file).__iter__())

    @staticmethod
    def _load_json(path: str) -> dict:
        with open(path, 'r') as file:
            return json.load(file)
