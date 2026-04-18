from pydantic import StringConstraints
from typing_extensions import Annotated

StrictStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
