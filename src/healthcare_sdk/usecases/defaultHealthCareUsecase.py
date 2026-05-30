from ..contracts import (
    ErrorDetail,
    MessageEnvelope,
    RawMessage,
    STATUS_DECODED,
    STATUS_ERROR,
    STATUS_NORMALIZED,
    STATUS_STORED,
    STATUS_VALIDATED,
)
from ..errors import DecodeError, NormalizationError, SdkError, StorageError, ValidationError


class DefaultHealthCareUsecase:
    """Built-in orchestrator that runs the decode→validate→normalize→store pipeline.

    Each stage is wrapped in error handling: SdkError subclasses are caught and
    recorded as ErrorDetail on the envelope; the pipeline stops at the failed stage
    and returns the envelope with status="error" instead of propagating exceptions.
    """

    def __init__(self, decoder, validator, normalizer, storage):
        self.decoder = decoder
        self.validator = validator
        self.normalizer = normalizer
        self.storage = storage

    def execute(self, raw_message: RawMessage) -> MessageEnvelope:
        envelope = MessageEnvelope.from_raw_message(raw_message)

        # --- Decode ---
        try:
            envelope.decoded_payload = self.decoder.decode(raw_message)
            envelope.status = STATUS_DECODED
        except SdkError as exc:
            envelope.errors.append(ErrorDetail(code=exc.code, message=exc.message, stage=exc.stage, context=exc.context))
            envelope.status = STATUS_ERROR
            return envelope
        except Exception as exc:
            envelope.errors.append(ErrorDetail(code="decode_error", message=str(exc), stage="decode"))
            envelope.status = STATUS_ERROR
            return envelope

        # --- Validate ---
        try:
            validation_result = self.validator.validate(envelope.decoded_payload)
            if not validation_result.is_valid:
                for err in validation_result.errors:
                    envelope.errors.append(err)
                if not validation_result.errors:
                    envelope.errors.append(ErrorDetail(code="validation_error", message="Validation failed", stage="validate"))
                envelope.status = STATUS_ERROR
                return envelope
            envelope.status = STATUS_VALIDATED
        except SdkError as exc:
            envelope.errors.append(ErrorDetail(code=exc.code, message=exc.message, stage=exc.stage, context=exc.context))
            envelope.status = STATUS_ERROR
            return envelope
        except Exception as exc:
            envelope.errors.append(ErrorDetail(code="validation_error", message=str(exc), stage="validate"))
            envelope.status = STATUS_ERROR
            return envelope

        # --- Normalize ---
        try:
            envelope.normalized_payload = self.normalizer.normalizeData(envelope.decoded_payload)
            envelope.status = STATUS_NORMALIZED
        except SdkError as exc:
            envelope.errors.append(ErrorDetail(code=exc.code, message=exc.message, stage=exc.stage, context=exc.context))
            envelope.status = STATUS_ERROR
            return envelope
        except Exception as exc:
            envelope.errors.append(ErrorDetail(code="normalization_error", message=str(exc), stage="normalize"))
            envelope.status = STATUS_ERROR
            return envelope

        # --- Store ---
        try:
            self.storage.save(envelope)
            envelope.status = STATUS_STORED
        except SdkError as exc:
            envelope.errors.append(ErrorDetail(code=exc.code, message=exc.message, stage=exc.stage, context=exc.context))
            envelope.status = STATUS_ERROR
            return envelope
        except Exception as exc:
            envelope.errors.append(ErrorDetail(code="storage_error", message=str(exc), stage="store"))
            envelope.status = STATUS_ERROR
            return envelope

        return envelope
