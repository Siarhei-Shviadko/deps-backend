import inspect

from fastapi.routing import APIRoute


class MarkerRoute(APIRoute):
    def __init__(self, *args, **kwargs) -> None:
        if inspect.isroutine(kwargs["endpoint"]) or inspect.isclass(kwargs["endpoint"]):
            name = kwargs["endpoint"].__name__
        else:
            name = kwargs["endpoint"].__class__.__name__

        if kwargs.get("openapi_extra"):
            visibility = kwargs["openapi_extra"]["visibility"]
            kwargs["summary"] = f"[{visibility.value}] {name.replace('_', ' ').title()}"

        super().__init__(*args, **kwargs)
