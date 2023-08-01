from typing import TypeVar, NoReturn, Optional
from pydantic import create_model, BaseModel

from db_settings.base import SettingsBase

TBaseSettings = TypeVar("TBaseSettings", bound=SettingsBase)


class _SettingsSchema:
    _generated: bool = False

    def schema(self, optional: bool = False) -> BaseModel:
        if self._generated is False:
            raise ValueError(
                "Use SettingsSchema"
                ".gen(`SyncSettingsBase / AsyncSettingsBase`) "
                "before include FastAPI router."
            )
        if optional:
            return self._schema_opt
        return self._schema

    def gen(self, input_settings: TBaseSettings) -> NoReturn:
        data_opt = {
            k: (Optional[v], None)
            for k, v in input_settings.__annotations__.items()
        }
        data = {k: (v, ...) for k, v in input_settings.__annotations__.items()}
        self._schema = create_model("Settings", **data)
        self._schema_opt = create_model("Settings", **data_opt)
        self._generated = True

    def __init__(self):
        self._schema = None
        self._schema_opt = None


SettingsSchema = _SettingsSchema()
DefaultResponse = create_model("DefaultResponse", status=(str, "ok"))
