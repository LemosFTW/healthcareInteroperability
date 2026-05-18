from dataclasses import dataclass, field
from typing import Iterable, List

from .repositories import HealthCareStorage
from .tools import AiHelper, Decoder, Normalizer, Validator
from .transportLayer import Adapter
from .usecases import HealthCareUsecase


class ComponentRegistrationError(ValueError):
    pass


@dataclass
class SdkComponents:
    adapters: List[Adapter] = field(default_factory=list)
    usecases: List[HealthCareUsecase] = field(default_factory=list)
    validators: List[Validator] = field(default_factory=list)
    decoders: List[Decoder] = field(default_factory=list)
    normalizers: List[Normalizer] = field(default_factory=list)
    aihelpers: List[AiHelper] = field(default_factory=list)
    storages: List[HealthCareStorage] = field(default_factory=list)

def _validate_components(components: Iterable[object], protocol_type: type, label: str) -> List[object]:
    validated: List[object] = []
    for component in components:
        if not isinstance(component, protocol_type):
            raise ComponentRegistrationError(
                f"{label} must implement {protocol_type.__name__} Protocol"
            )
        validated.append(component)
    return validated


def register_components(
    adapters: Iterable[Adapter] = (),
    usecases: Iterable[HealthCareUsecase] = (),
    validators: Iterable[Validator] = (),
    decoders: Iterable[Decoder] = (),
    normalizers: Iterable[Normalizer] = (),
    aihelpers: Iterable[AiHelper] = (),
    storages: Iterable[HealthCareStorage] = (),
) -> SdkComponents:
    return SdkComponents(
        adapters=_validate_components(adapters, Adapter, "Adapters"),
        usecases=_validate_components(usecases, HealthCareUsecase, "Usecases"),
        validators=_validate_components(validators, Validator, "Validators"),
        decoders=_validate_components(decoders, Decoder, "Decoders"),
        normalizers=_validate_components(normalizers, Normalizer, "Normalizers"),
        aihelpers=_validate_components(aihelpers, AiHelper, "AiHelpers"),
        storages=_validate_components(storages, HealthCareStorage, "Storages"),
    )
