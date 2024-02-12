import os
from configparser import ConfigParser
from functools import cache

LOCAL_CONFIG_PATH = "config/application_conf.ini"
DOCKER_APP_CONFIG_PATH = "config/docker_application_conf.ini"
TESTING_ENV_CONFIG_PATH = "config/test_application_conf.ini"


@cache
class AppSettings:
    def __init__(self):
        """
        This class will handle all the configuration for the application.
        ADD HERE all the configuration that you need to use in the application.

        OPEN CLOSE PRINCIPLE:
          - Only create a new class attribute and read from the configuration file.
        """
        self.settings = None
        self.setup()
        self.API_PORT = self.settings.get("app", "api_port")
        self.API_HOST = self.settings.get("app", "api_host")

        self.DATABASE_HOST = self.settings.get("database", "host")
        self.DATABASE_PORT = self.settings.get("database", "port")
        self.DATABASE_USER = self.settings.get("database", "user")
        self.DATABASE_PASSWORD = self.settings.get("database", "password")
        self.DATABASE_NAME = self.settings.get("database", "dbname")
        self.DATABASE_POOL_SIZE = self.settings.get("database", "pool_size")
        self.DATABASE_URL = f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        self.DATABASE_URL_ASYNC = f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    def setup(self):
        config_file_to_use = LOCAL_CONFIG_PATH
        environment = os.getenv("ENV")

        if environment == "docker":
            print(f"Using docker config file {DOCKER_APP_CONFIG_PATH}")
            config_file_to_use = DOCKER_APP_CONFIG_PATH
        elif environment == "test":
            print(f"Using testing config file {TESTING_ENV_CONFIG_PATH}")
            config_file_to_use = TESTING_ENV_CONFIG_PATH
        elif environment == "local":
            print(f"Using local config file {LOCAL_CONFIG_PATH}")
        else:
            print(f"No environment set, using default config file {LOCAL_CONFIG_PATH}")

        self.settings = ConfigParser()
        self.settings.read(config_file_to_use)


APP_SETTINGS = AppSettings()
