import os
import importlib
from types import FunctionType

def register_all_handlers(client, logger):
    handlers_dir = os.path.dirname(__file__)
    files = sorted(f for f in os.listdir(handlers_dir)
                   if f.endswith(".py") and f != "__init__.py")

    for filename in files:
        module_name = f"handlers.{filename[:-3]}"
        command_name = filename[:-3]
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"\033[91mОшибка импорта {command_name}: {e}\033[0m")
            continue

        register_func = getattr(module, "register", None)
        if isinstance(register_func, FunctionType):
            try:
                register_func(client)
                logger.info(f"\033[92mКоманда \033[93m{command_name}\033[92m зарегистрирована\033[0m")
            except Exception as e:
                logger.error(f"\033[91mОшибка в register() команды {command_name}: {e}\033[0m")
        else:
            logger.warning(f"\033[93mФайл {command_name} не содержит функцию register\033[0m")