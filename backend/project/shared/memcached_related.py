from pymemcache.client.base import PooledClient
from pymemcache import serde

MEMCACHED_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 11211
}

#Connection to memcached on given port and host.
memcached_client = PooledClient((MEMCACHED_CONFIG["HOST"], MEMCACHED_CONFIG["PORT"]), serde.pickle_serde)