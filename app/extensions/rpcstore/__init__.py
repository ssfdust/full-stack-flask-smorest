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

from kombu import Exchange, Queue


class AMQPStore(object):

    def __init__(self, key, value=None, exchange=None, expires=None,
                 requeue=False, limit=999, routing_key=None, auto_delete=False):
        self.key = key
        self.requeue = requeue
        self.limit = limit
        self.value = value
        self.values = []
        if exchange is None and '_' in key:
            exchange = key.split('_')[0]
        self.exchange = Exchange(exchange)
        if not routing_key:
            routing_key = key
        self.routing_key = routing_key
        self.queue = Queue(self.key, self.exchange, durable=True,
                           routing_key=self.routing_key, auto_delete=auto_delete,
                           expires=expires)

    def save(self, expiration=None):
        from kombu import Connection
        from flask import current_app
        from kombu.pools import producers

        conn = Connection(current_app.config['CELERY_BROKER_URL'], heartbeat=0)

        with producers[conn].acquire(block=True) as producer:
            producer.publish(
                self.value,
                exchange=self.exchange,
                routing_key=self.routing_key,
                correlation_id=self.routing_key,
                serializer='json',
                retry=True,
                declare=[self.queue],
                delivery_mode=2,
                expiration=expiration
            )

        return self.value

    def reload(self, no_ack=False):
        self.value = None
        msgs = []
        self.values = []
        for i in self._reload():
            self.value = i.payload
            self.values.append(self.value)
            msgs.append(i)

        if no_ack is False:
            for i in msgs:
                i.ack()

        return self.value

    def _reload(self, no_ack=False):
        from kombu import Connection, pools
        from flask import current_app
        conn = Connection(current_app.config['CELERY_BROKER_URL'], heartbeat=0)
        pool = pools.connections[conn]

        with pool.acquire_channel(block=True) as (_, channel):
            binding = self.queue(channel)

            for _ in range(self.limit):
                msg = binding.get(accept=['json'], no_ack=no_ack)
                if not msg:
                    break
                yield msg
