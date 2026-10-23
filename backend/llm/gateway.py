"""Small capability-aware gateway; never falls back from local to hosted implicitly."""

from dataclasses import dataclass
from enum import StrEnum


class Provider(StrEnum):
    MOCK = "mock"
    OLLAMA = "ollama"
    HOSTED = "hosted"


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: Provider
    model: str
    allows_hosted_data: bool = False
    supports_tools: bool = False
    supports_structured_output: bool = False


class ModelGatewayError(RuntimeError):
    pass


class ModelGateway:
    def __init__(self, profiles: dict[str, ModelProfile] | None = None) -> None:
        self.profiles = profiles or {"mock": ModelProfile("mock", Provider.MOCK, "deterministic")}

    def generate(self, profile_name: str, prompt: str, *, contains_sensitive_data: bool = False) -> str:
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ModelGatewayError("Unknown model profile.")
        if contains_sensitive_data and profile.provider is Provider.HOSTED and not profile.allows_hosted_data:
            raise ModelGatewayError("Profile forbids sending sensitive data to a hosted provider.")
        if profile.provider is Provider.MOCK:
            return "Mock generation: use cited evidence and state limitations."
        raise ModelGatewayError(f"Provider '{profile.provider}' is configured but not available in this environment.")
