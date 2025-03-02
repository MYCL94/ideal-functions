import pytest
from src.application.DataManager import DataManager, DatasetType

@pytest.fixture
def simulated_data_manager():
    """Fixture to create a test DataManager object."""
    yield DataManager(dataset_name='Testdata',
                      database_name='Testdatabase')
        
@pytest.mark.parametrize('dataset_type', DatasetType)
def test_load_data(simulated_data_manager: DataManager, dataset_type) -> None:
    """Test the load_data method of DataManager."""
    simulated_data_manager.load_data(dataset_type)


def test_load_invalid_data(simulated_data_manager: DataManager) -> None:
    """Test the load_data method with an invalid dataset type."""
    with pytest.raises(AttributeError):
        simulated_data_manager.load_data('invalid_data')

@pytest.mark.parametrize('dataset_type', DatasetType)
def test_read_data_from_table(simulated_data_manager: DataManager, dataset_type) -> None:
    """Test the read_data_from_table method of DataManager."""
    simulated_data_manager.load_data(dataset_type)
    if dataset_type == DatasetType.TRAIN:
        table_name = 'TrainingData'
    elif dataset_type == DatasetType.IDEAL:
        table_name = 'IdealFunctions'
    elif dataset_type == DatasetType.TEST:
        table_name = 'TestData'
    simulated_data_manager.read_data_from_table(table_name)

@pytest.mark.parametrize('dataset_type', DatasetType)
def test_read_invalid_data_from_table(simulated_data_manager: DataManager, dataset_type) -> None:
    """Test the read_data_from_table method with an invalid table name."""
    simulated_data_manager.load_data(dataset_type)
    with pytest.raises(Exception):
        simulated_data_manager.read_data_from_table('invalid_data')

@pytest.mark.parametrize('dataset_type', DatasetType)
def test_save_data(simulated_data_manager: DataManager, dataset_type) -> None:
    """Test the save_data method of DataManager."""
    data_frame = simulated_data_manager.load_data(dataset_type)
    simulated_data_manager.save_data(dataset_type.value, data_frame)

@pytest.mark.parametrize('dataset_type', DatasetType)
def test_save_invalid_data(simulated_data_manager: DataManager, dataset_type) -> None:
    """Test the save_data method with an invalid table name."""
    invalid_data = [2,2]
    with pytest.raises(AttributeError):
        simulated_data_manager.save_data(dataset_type.value, invalid_data)