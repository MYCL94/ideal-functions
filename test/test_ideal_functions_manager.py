import shutil
from pathlib import Path
import pandas as pd
import pytest
from src.application.IdealFunctionsManager import IdealFunctionsManager, DatasetType
from src.application.DataManager import DataManager


@pytest.fixture(scope='module')
def simulated_ideal_functions_manager():
    """Fixture to create a simulated IdealFunctionsManager instance for testing."""
    TEST_DATA_DIR = Path('./test/temp')
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    yield IdealFunctionsManager(dataset_name='Testdata')

    shutil.rmtree(str(TEST_DATA_DIR.absolute()), ignore_errors=True)

@pytest.fixture(scope='module')
def sample_data():
    """Fixture to create sample data for testing."""
    data = {
        'x': [1, 2, 3, 4, 5],
        'train_y1': [6, 7, 8, 9, 10],
        'train_y2': [1, 3, 5, 7, 9],
        'ideal_y1': [1.2, 3.4, 5.6, 7.8, 9.0],
        'ideal_y2': [2.1, 4.3, 6.5, 8.7, 10.9],
        'y': [1,2,3,4,5]
    }
    return pd.DataFrame(data)

def test_init_databases_success(simulated_ideal_functions_manager:IdealFunctionsManager):
    """Test if _init_databases initializes DataManager instances correctly."""
    assert isinstance(simulated_ideal_functions_manager.data_manager, DataManager)
    assert isinstance(simulated_ideal_functions_manager.results_db, DataManager)

@pytest.mark.parametrize('dataset_type', DatasetType)
def test__load_data(simulated_ideal_functions_manager: IdealFunctionsManager, dataset_type) -> None:
    """Test if _load_data loads data correctly."""
    loaded_data = simulated_ideal_functions_manager._load_data(dataset_type)
    assert isinstance(loaded_data, pd.DataFrame)
    assert not loaded_data.empty

def test__calculate_squared_deviation(simulated_ideal_functions_manager: IdealFunctionsManager, sample_data) -> None:
    """Test if _calculate_squared_deviation calculates correctly."""
    x = sample_data['x']
    train_y = sample_data['train_y1']
    ideal_func = sample_data['ideal_y1']

    deviation = simulated_ideal_functions_manager._calculate_squared_deviation(train_y, ideal_func, x)
    assert isinstance(deviation, float)
    assert deviation >= 0

def test__calculate_squared_deviation_exception(simulated_ideal_functions_manager: IdealFunctionsManager):
    """Test _calculate_squared_deviation handles exceptions during calculation."""
    with pytest.raises(Exception):
        simulated_ideal_functions_manager._calculate_squared_deviation(pd.Series([1,2,3]),pd.Series([1,2]), 'invalid')

def test_get_all_visualizations_success(simulated_ideal_functions_manager:IdealFunctionsManager):
    """Test all functions with successful data loading and visualization."""
    simulated_ideal_functions_manager.get_all_functions_visualized()

def test_get_ideal_functions_success(simulated_ideal_functions_manager:IdealFunctionsManager):
    """Test get_ideal_functions with successful data loading and visualization."""
    simulated_ideal_functions_manager.get_ideal_functions()
    assert isinstance(simulated_ideal_functions_manager.ideal_functions_selection, dict)
    assert isinstance(simulated_ideal_functions_manager.ideal_functions_data, pd.DataFrame)
    assert len(simulated_ideal_functions_manager.ideal_functions_data.columns) > 0

def test__store_results_success(simulated_ideal_functions_manager:IdealFunctionsManager, sample_data:pd.DataFrame):
    """Test if _store_results stores results correctly."""
    simulated_ideal_functions_manager._store_results(sample_data)

def test_map_test_data_to_ideal_functions_success(simulated_ideal_functions_manager:IdealFunctionsManager):
    """Test map_test_data_to_ideal_functions successfully.""" 
    simulated_ideal_functions_manager.get_ideal_functions()
    simulated_ideal_functions_manager.map_test_data_to_ideal_functions()