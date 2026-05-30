from ..contracts import (
    MessageEnvelope,
    RawMessage,
    STATUS_DECODED,
    STATUS_NORMALIZED,
    STATUS_STORED,
    STATUS_VALIDATED,
)


class DefaultHealthCareUsecase:
    """Built-in orchestrator that runs the decode→validate→normalize→store pipeline."""

    def __init__(self, decoder, validator, normalizer, storage):
        self.decoder = decoder
        self.validator = validator
        self.normalizer = normalizer
        self.storage = storage

    def execute(self, raw_message: RawMessage) -> MessageEnvelope:
        envelope = MessageEnvelope.from_raw_message(raw_message)

        envelope.decoded_payload = self.decoder.decode(raw_message)
        envelope.status = STATUS_DECODED

        self.validator.validate(envelope.decoded_payload)
        envelope.status = STATUS_VALIDATED

        envelope.normalized_payload = self.normalizer.normalizeData(envelope.decoded_payload)
        envelope.status = STATUS_NORMALIZED

        self.storage.save(envelope)
        envelope.status = STATUS_STORED

        return envelope
