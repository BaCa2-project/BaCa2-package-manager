import requests
from pkg_resources import parse_version

MANUAL_VERSION = None


def list_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"

    res = requests.get(url, timeout=20)

    data = res.json()
    versions = data['releases']

    return sorted(versions, key=parse_version, reverse=True)


def version(new_version: bool = False) -> str:
    """
    Returns version of the new package, by elevating the version of the old package. Or returns the
    manual version.
    """
    versions = list_versions('baca2-package-manager')
    v = versions[0]
    if len(versions) == 0:
        v = '0.0.1'

    if not new_version:
        return v

    if MANUAL_VERSION is not None:
        mv = MANUAL_VERSION
        if mv not in versions:
            v = mv

    new_v = v.split('.')
    new_v[-1] = str(int(new_v[-1]) + 1)
    new_v = '.'.join(new_v)
    return new_v


if __name__ == '__main__':
    print(version(new_version=True))