from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .executor import Executor


@dataclass
class OSInfo:
    id: str
    version_id: str
    pretty_name: str

    def is_supported(self) -> bool:
        if self.id not in {"ubuntu", "debian"}:
            return False
        if self.id == "ubuntu":
            return self.version_id in {"20.04", "22.04", "24.04"}
        if self.id == "debian":
            # Accept stable-like versions (11, 12)
            return bool(re.match(r"^(11|12)(\\.\\d+)?$", self.version_id))
        return False


def detect_os(executor: Executor) -> Optional[OSInfo]:
    code, out, _ = executor.run("cat /etc/os-release")
    if code != 0:
        return None
    data = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k] = v.strip().strip('"')
    return OSInfo(
        id=data.get("ID", ""),
        version_id=data.get("VERSION_ID", ""),
        pretty_name=data.get("PRETTY_NAME", ""),
    )
