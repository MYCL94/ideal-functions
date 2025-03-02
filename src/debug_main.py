import logging
from src.application.IdealFunctionsManager import IdealFunctionsManager

if __name__ == "__main__":
    logger_config = logging.basicConfig(level=logging.INFO)
    ideal_functions_manager = IdealFunctionsManager(dataset_name='Dataset1')
    ideal_functions_manager.get_ideal_functions()
    ideal_functions_manager.map_test_data_to_ideal_functions()