from hashlib import sha256
import re

import pydantic


class BacaToBroker(pydantic.BaseModel):
    pass_hash: str
    submit_id: str
    package_path: str
    commit_id: str
    submit_path: str


class TestResult(pydantic.BaseModel):
    name: str
    status: str
    time_real: float = 0.0
    time_cpu: float = 0.0
    runtime_memory: int = 0
    answer: str = ''

    logs: dict[str, str] = {}


class SetResult(pydantic.BaseModel):
    name: str
    tests: dict[str, TestResult]


class BrokerToBaca(pydantic.BaseModel):
    pass_hash: str
    submit_id: str
    results: dict[str, SetResult]


class BrokerToBacaError(pydantic.BaseModel):
    pass_hash: str
    submit_id: str
    error_id: str = '0'
    error_data: dict[str, str]


def create_broker_submit_id(course_name: str, submit_id: int) -> str:
    return f'{course_name}___{submit_id}'


def split_broker_submit_id(broker_submit_id: str) -> tuple[str, int]:
    r = re.compile(r'([-A-Za-z0-9.,_]+)___([0-9]+)')
    m = re.fullmatch(r, broker_submit_id)
    course_name = m.group(1)
    submit_id = int(m.group(2))
    return course_name, submit_id


def make_hash(password: str, broker_submit_id: str) -> str:
    hash_obj = sha256()
    hash_obj.update((password + '___').encode('utf-8'))
    hash_obj.update(broker_submit_id.encode('utf-8'))
    return hash_obj.hexdigest()
