from project.main import app
from project.models import Permission
# from pymemcache.client.base import PooledClient
# from pymemcache import serde
# from project.config import MEMCACHED_CONFIG

# client = PooledClient((MEMCACHED_CONFIG["HOST"], MEMCACHED_CONFIG["PORT"]), serde.pickle_serde)

# @app.post("/createPermission")
# async def create_permission():
#     await Permission.create(**{"permissions": {}})
#     client.set('user', 50)
#     print(client.get('user'))
#     return None