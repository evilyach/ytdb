from pydantic import ValidationError
from pydantic_core import Url


def validate_url(url: str) -> bool:
    try:
        Url(url)
        return True
    except ValidationError as error:
        return False
