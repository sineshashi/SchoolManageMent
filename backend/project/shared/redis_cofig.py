import redis.asyncio as redis
import pickle, json

redis_url = "rediss://red-ccemk2en6mpt4gqtfhtg:1dR8SmnglukCwSNePB55SwhKCAqDw2fz@singapore-redis.render.com:6379"
r = redis.Redis.from_url(redis_url)

def serialize(data, jsonify=False, picklify =False, stringfy=False):
    if stringfy:
        try:
            return str(data)
        except Exception as e:
            raise e
    if jsonify:
        try:
            return json.dumps(data)
        except Exception as e:
            raise e
    if picklify:
        try:
            return pickle.dumps(data)
        except Exception as e:
            raise e

def deserialize(data, jsonify=False, picklify =False):
    if jsonify:
        try:
            return json.loads(data)
        except Exception as e:
            raise e
    if picklify:
        try:
            return pickle.loads(data)
        except Exception as e:
            raise e

async def set_in_redis(
    key=None,
    value =None,
    key_value_pairs = None,
    key_value_hash_map = None,
    expiry_time=None,
    conn=r,
    transaction=True,
    pickle_value = True,
    json_value = False
    ):
    '''
    pass a python dict in key_value_hash_map to set key as key and value as value..
    pass key and value to set key and value.
    pass key value pairs as a list of tuples and many = True to set many values at once.
    expiry_time must be in seconds which sets the key value pair with the expiry time.
    pass redis url to set value in different redis instance.
    transaction=True means transactions will be atomic.
    json_value = True will jsonify the values and make sure you use same in the case of get.
    pickle_value = True will use pickle the value and make sure you use the same in the case of get.
    If both json_value and pickle_value are false, will try to convert into string and save.

    Keys will be converted to string and value will be serialized to serde.
    '''

    if pickle_value and json_value:
        raise redis.DataError("Both json and pickle can not be true.")
 
    try:    
        async with conn.pipeline(transaction=transaction) as pipe:
            if key is not None:
                key = str(key)
                value = serialize(value, picklify=True, jsonify=json_value, stringfy=pickle_value and json_value)
                if expiry_time is not None:
                    await pipe.setex(key, expiry_time, value)
                else:
                    await pipe.set(key, value)

            if key_value_pairs is not None:
                for (key, value) in key_value_pairs:
                    key = str(key)
                    value = serialize(value, picklify=True, jsonify=json_value, stringfy=pickle_value and json_value)
                    if expiry_time is not None:
                        await pipe.setex(key, expiry_time, value )
                    else:
                        await pipe.set(key, value)
            
            if key_value_hash_map is not None:
                for key, value in key_value_hash_map.items():
                    key = str(key)
                    value = serialize(value, picklify=pickle_value, jsonify=json_value, stringfy=pickle_value and json_value)
                    if expiry_time is not None:
                        await pipe.setex(key, expiry_time, value )
                    else:
                        await pipe.set(key, value)
            res = await pipe.execute()
        for resp in res:
            assert resp

        return True

    except Exception as e:
        raise e

async def get_from_redis(
    key = None,
    keys = None,
    json_value = False,
    pickle_value = True,
    transaction = True,
    conn = r
    ):
    '''
    pass key or keys to get the values.
    pass conn as a redis connection to set value in different redis instance.
    transaction=True means transactions will be atomic.
    json_value = True will jsonify the values and make sure you use same in the case of get.
    pickle_value = True will use pickle the value and make sure you use the same in the case of get.
    If both json_value and pickle_value are false, will try to convert into string and save.
    Keys will be converted to string and values will be serialized to pickle.
    '''
    if pickle_value and json_value:
        raise redis.DataError("Both json and pickle can not be true.")
    
    if key is not None and keys is not None:
        raise redis.DataError("Both key and keys can not be passed simulatneously.")

    input_key = key

    try:
        async with conn.pipeline(transaction=transaction) as pipe:
            if key is not None:
                key = str(key)
                await pipe.get(key)
            if keys is not None:
                for key in keys:
                    await pipe.get(key)
            values = await pipe.execute()
        values_to_be_returned = []
        for value in values:
            if value is None:
                values_to_be_returned.append(value)
            else:
                value = deserialize(value, picklify=pickle_value, jsonify=json_value)
                values_to_be_returned.append(value)

        if input_key is not None:
            return values_to_be_returned[0]
        else:
            return values_to_be_returned

    except Exception as e:
        raise e

async def delete_from_redis(
    key = None,
    keys = None,
    transaction = True,
    conn = r
    ):
    try:
        async with conn.pipeline(transaction=transaction) as pipe:
            if key is not None:
                key = str(key)
                await pipe.delete(key)
            if keys is not None:
                for key in keys:
                    await pipe.delete(key)
            res = await pipe.execute()
            for resp in res:
                assert resp

        return True

    except Exception as e:
        raise e