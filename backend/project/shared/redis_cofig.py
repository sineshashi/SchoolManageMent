import redis

redis_url = "rediss://red-ccemk2en6mpt4gqtfhtg:1dR8SmnglukCwSNePB55SwhKCAqDw2fz@singapore-redis.render.com:6379"
redis_port = 6379

r = redis.Redis.from_url(redis_url, decode_responses=True)