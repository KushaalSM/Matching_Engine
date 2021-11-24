import redis
import json

class RedisDB:
    def __init__(self, config) -> None:
        self.config = config
        self.db = None

    def create_connections(self):
        self.db = redis.StrictRedis(host=self.config['host'], port=self.config['port'], db=self.config['db_number'])
        return

    def destroy_connections(self):
        self.db.close()
        return

    def get_pubsub_client(self, pattern):
        keyspace_pattern = f"__keyspace@{self.config['db_number']}__:{pattern}*"
        pubsub_client = self.db.pubsub(ignore_subscribe_messages=True)
        pubsub_client.psubscribe(keyspace_pattern)
        return pubsub_client
    
    def get_value(self, key):
        if not self.db.exists(key):
            # If key does not exist in the database.
            return None
        if self.db.type(key) == 'string':
            return self.db.get(key)
        if self.db.type(key) == 'hash':
            return self.db.hgetall(key)
        return

    def extract_data_from_pubsub_message(self, message):
        key = message.split(':')[-1]
        value = self.db.get(name=key)
        if not value == None:
            return json.loads(value)
        return {}