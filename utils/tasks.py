from taskiq import TaskiqRedisBroker

# Broker definition for Taskiq. Redis container will be used as the broker.
# The URL matches the service name defined in docker-compose.yml
broker = TaskiqRedisBroker("redis://redis:6379/0")
