from dotenv import load_dotenv, dotenv_values

load_dotenv()

config_vars = dotenv_values()

for key, value in config_vars.items():
  globals()[key] = value
