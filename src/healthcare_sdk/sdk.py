import inspect
from dataclasses import dataclass, field
from typing import Iterable, List, Set

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


def _protocol_members(protocol_type: type) -> Set[str]:
    try:
        from typing import get_protocol_members  # Python 3.12+
        return get_protocol_members(protocol_type)
    except ImportError:
        return getattr(protocol_type, "__protocol_attrs__", set())


def _required_param_count(method) -> int:
    """Return the number of required positional parameters, excluding self."""
    try:
        sig = inspect.signature(method)
    except (ValueError, TypeError):
        return 0
    return sum(
        1
        for name, p in sig.parameters.items()
        if name != "self"
        and p.default is inspect.Parameter.empty
        and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    )


def _check_signatures(component: object, protocol_type: type, label: str) -> None:
    """Raise ComponentRegistrationError if any Protocol method has incompatible arity."""
    for method_name in _protocol_members(protocol_type):
        proto_method = getattr(protocol_type, method_name, None)
        comp_method = getattr(component, method_name, None)
        if proto_method is None or comp_method is None or not callable(proto_method):
            continue

        proto_required = _required_param_count(proto_method)
        comp_required = _required_param_count(comp_method)

        if comp_required < proto_required:
            raise ComponentRegistrationError(
                f"{label}: method '{method_name}' has incompatible signature — "
                f"expected {proto_required} required parameter(s) per "
                f"{protocol_type.__name__} Protocol, "
                f"but component defines {comp_required}."
            )


def _validate_components(
    components: Iterable[object], protocol_type: type, label: str
) -> List[object]:
    validated: List[object] = []
    for component in components:
        if not isinstance(component, protocol_type):
            raise ComponentRegistrationError(
                f"{label} must implement {protocol_type.__name__} Protocol"
            )
        _check_signatures(component, protocol_type, label)
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
