# Copyright 2019 RedLotus <ssfdust@gmail.com>
# Author: RedLotus <ssfdust@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import request, url_for
import functools
import marshmallow as ma


class PaginationParametersSchema(ma.Schema):

    class Meta:
        ordered = True

    page = ma.fields.Integer(missing=1, validate=ma.validate.Range(min=1))
    per_page = ma.fields.Integer(
        missing=10, validate=ma.validate.Range(min=1, max=100))


def paginate(max_per_page=10):

    def decorator(func):
        parameters = {
            'in': 'query',
            'schema': PaginationParametersSchema,
        }

        # Add pagination params to doc info in function object
        func._apidoc = getattr(func, '_apidoc', {})
        func._apidoc.setdefault('parameters', []).append(parameters)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', max_per_page, type=int)
            query = func(*args, **kwargs)
            p = query.paginate(page, per_page)

            meta = {
                'page': page,
                'per_page': per_page,
                'total': p.total,
                'pages': p.pages,
            }

            links = {}
            if p.has_next:
                links['next'] = url_for(
                    request.endpoint,
                    page=p.next_num,
                    per_page=per_page,
                    **kwargs)
            if p.has_prev:
                links['prev'] = url_for(
                    request.endpoint,
                    page=p.prev_num,
                    per_page=per_page,
                    **kwargs)
            links['first'] = url_for(
                request.endpoint, page=1, per_page=per_page, **kwargs)
            links['last'] = url_for(
                request.endpoint, page=p.pages, per_page=per_page, **kwargs)

            meta['links'] = links
            # logging.warning(p.items[0].members.all())
            result = {'data': p.items, 'meta': meta, 'code': 0}

            return result

        return wrapped

    return decorator
