# This config makes env variables easier to import
# Reference: https://www.python-engineer.com/posts/dotenv-python/
from dotenv import load_dotenv, dotenv_values

# Load environment variables from a .env file into the environment
load_dotenv()

# Retrieve the environment variables as a dictionary
config_vars = dotenv_values()

# Assign each environment variable to a global variable
for key, value in config_vars.items():
    globals()[key] = value
