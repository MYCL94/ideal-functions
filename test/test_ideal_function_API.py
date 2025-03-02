import os
import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK
from src.application.DataManager import DatasetType
from src.application.Visualizer import VisualizationName
from application.rest.ideal_functions_API import app

#Constants
TEST_DATASET_NAME ='Testdata'
os.environ['DATASET_NAME'] = TEST_DATASET_NAME

@pytest.fixture(scope='module')
def client():
    """Fixture to create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.asyncio
async def test_root_endpoint(client:TestClient):
    """Test the root endpoint of the API."""
    response = client.get('/')
    assert response.status_code == HTTP_200_OK
    assert TEST_DATASET_NAME in response.text

@pytest.mark.asyncio
async def test_swagger_ui_html(client:TestClient):
    """Test the swagger UI endpoint."""
    response = client.get('/docs')
    assert response.status_code == HTTP_200_OK
    assert 'Swagger UI' in response.text

@pytest.mark.asyncio
async def test_redoc_html(client:TestClient):
    """Test the Redoc UI endpoint."""
    response = client.get('/redoc')
    assert response.status_code == HTTP_200_OK
    assert 'ReDoc' in response.text

@pytest.mark.asyncio
async def test_select_ideal_functions(client:TestClient):
    """Test the select_ideal_functions endpoint."""
    response = client.post('/v1/ideal-functions/select')
    assert response.status_code == HTTP_200_OK
    assert response.json()['message'] == 'Ideal function selection completed successfully.'
    assert 'selected_functions' in response.json()

@pytest.mark.asyncio
async def test_map_test_data(client:TestClient):
    """Test the map_test_data endpoint."""
    response = client.post('/v1/test-data/map')
    assert response.status_code == HTTP_200_OK
    assert response.json()['message'] == 'Test data mapping completed.'
    assert 'mapping_summary' in response.json()

@pytest.mark.asyncio
async def test_get_visualization(client:TestClient):
    """Test the get_visualization endpoint."""
    response = client.get(f'/v1/visualizations/{VisualizationName.initial_data.value}')
    assert response.status_code == HTTP_200_OK

@pytest.mark.asyncio
@pytest.mark.parametrize("dataset_type", DatasetType)
async def test_get_database(client:TestClient, dataset_type):
    """Test the get_database endpoint."""
    response = client.get(f'/v1/data/database-view?dataset_type={dataset_type.value}')
    assert response.status_code == HTTP_200_OK
    assert 'Database view with FastAPI' in response.text
    
@pytest.mark.asyncio
@pytest.mark.parametrize("dataset_type", DatasetType)
async def test_load_data(client:TestClient, dataset_type):
    """Test the get_database endpoint."""
    response = client.get(f'/v1/data/load-data?dataset_type={dataset_type.value}')
    assert response.status_code == HTTP_200_OK

@pytest.mark.asyncio
async def test_get_all_visualizations(client:TestClient):
    """Test the get_all_visualizations endpoint."""
    response = client.get('/v1/visualizations/all')
    assert response.status_code == HTTP_200_OK

@pytest.mark.asyncio
async def test_get_test_mapping_results(client:TestClient):
    """Test the get_test_mapping_results endpoint."""
    response = client.get('/v1/data/test-mapping-results')
    assert response.status_code == HTTP_200_OK
    assert 'Database view with FastAPI: Test Data Mapping' in response.text
