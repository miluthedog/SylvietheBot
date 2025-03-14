from os import environ
from dotenv import load_dotenv, dotenv_values

load_dotenv()

env_vars = dotenv_values(".env")

secret = {**env_vars, **environ}


class ID:
    main = 1242439205406244954
    voice = 1249733414601625610

    administrator = [
        754703228003942522,  # Pha
        754703510360162425  # Pha con
    ]


class token:
    discord = secret.get("DISCORDTOKEN")

