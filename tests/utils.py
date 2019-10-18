import json
from collections import OrderedDict

from werkzeug.utils import cached_property
from flask import Response

class JSONResponse(Response):
    """
    A Response class with extra useful helpers, i.e. ``.json`` property.

    来源：https://github.com/frol/flask-restplus-server-example/
    """
    # pylint: disable=too-many-ancestors

    @cached_property
    def json(self):
        return json.loads(
            self.get_data(as_text=True),
            object_pairs_hook=OrderedDict
        )
