import re


def ipv4_addr_check(addr: str) -> bool:
    p = re.compile(
        "^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$"
    )
    if p.match(addr):
        return True
    else:
        return False
