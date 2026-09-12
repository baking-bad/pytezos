from contextlib import suppress
from datetime import datetime
from datetime import time
from datetime import timezone
from typing import Any
from typing import Type

import dateutil.parser
from cattr import Converter


def structure_datetime(obj: Any, cls: Type) -> datetime:
    with suppress(ValueError, TypeError):
        return datetime.utcfromtimestamp(float(obj)).replace(tzinfo=timezone.utc)
    with suppress(dateutil.parser.ParserError):
        return dateutil.parser.parse(obj)
    raise ValueError


def unstructure_datetime(obj: datetime) -> float:
    return obj.timestamp()


def structure_time(obj: Any, cls: Type) -> time:
    return time.fromisoformat(obj)


converter = Converter()
converter.register_structure_hook(datetime, structure_datetime)
converter.register_unstructure_hook(datetime, unstructure_datetime)
converter.register_structure_hook(time, structure_time)
