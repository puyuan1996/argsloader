from typing import Tuple

from .base import BaseUnit, _UnitProcessProxy, _to_unit
from ..base import ParseResult, PValue


class PipeUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units: Tuple[BaseUnit, ...] = tuple(map(_to_unit, (unit, *units)))

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        curv, rs, valid = v, [], True
        for i, unit in enumerate(self._units):
            if valid:
                curv = unit._process(curv)
                rs.append(curv)
                if not curv.status.valid:
                    valid = False
            else:
                rs.append(unit._skip(v))

        if valid:
            return proxy.success(curv, rs)
        else:
            return proxy.error(None, rs)

    @classmethod
    def pipe(cls, *units):
        actual_units = []
        for unit in units:
            if isinstance(unit, PipeUnit):
                for iu in unit._units:
                    actual_units.append(iu)
            else:
                actual_units.append(unit)

        return PipeUnit(*actual_units)


def pipe(*units) -> PipeUnit:
    return PipeUnit.pipe(*units)
