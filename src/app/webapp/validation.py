class InvalidUserPayload(ValueError):
    """Raised when the user payload is missing or malformed."""


def parse_user_payload(payload: object) -> tuple[str, int]:
    if not isinstance(payload, dict):
        raise InvalidUserPayload("invalid user payload")

    nome = payload.get("nome")
    idade = payload.get("idade")

    if not isinstance(nome, str) or not nome.strip():
        raise InvalidUserPayload("invalid user payload")

    try:
        normalized_age = int(idade)
    except (TypeError, ValueError) as exc:
        raise InvalidUserPayload("invalid user payload") from exc

    return nome.strip(), normalized_age
