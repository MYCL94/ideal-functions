from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os
from pathlib import Path

from src.application.DataManager import DatasetType
from src.application.Visualizer import VisualizationName
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from src.application.IdealFunctionsManager import IdealFunctionsManager

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    global dataset_name
    global ideal_function_manager

    dataset_name = os.environ['DATASET_NAME'] if 'DATASET_NAME' in os.environ else 'Dataset1'
    ideal_function_manager = IdealFunctionsManager(dataset_name=dataset_name)
    yield

app = FastAPI(
    title='ideal-functions-app',
    description='[ideal-functions-API]',
    lifespan=lifespan
)

# Static files to display Swagger , Redoc UI and Stylesheet for pandas Tableview.
app.mount('/static', StaticFiles(directory='./src/application/rest/static'),
          name='static')

@app.get('/', tags=['Root'])
async def root(request: Request) -> HTMLResponse:
    """Gets the root endpoint of the service.

    Returns:
        A HTMLResponse with a standard message.
    """
    return HTMLResponse(content=f'ideal-functions-API is running. Selected dataset: {dataset_name}', status_code=200)


@app.get('/docs', include_in_schema=False, response_class=HTMLResponse)
async def swagger_ui_html() -> HTMLResponse:
    """Creates SWAGGER UI HTML page.
    Adopted from:
    https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/#disable-the-automatic-docs-for-static-files

    Returns:
        Customized SWAGGER HTML using static resources.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url[1:],
        title=f'{app.title} - Swagger UI',
        oauth2_redirect_url=f'/localhost{app.swagger_ui_oauth2_redirect_url}',
        swagger_js_url='static/swagger-ui-bundle.js',
        swagger_css_url='static/swagger-ui.css',
        init_oauth={'clientId': 'swagger-ui'}
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html() -> HTMLResponse:
    """Creates ReDoc HTML page.
    Adopted from:
    https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/#disable-the-automatic-docs-for-static-files
    Returns:
        Customized ReDoc HTML using static resources.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url[1:],
        title=f'{app.title} - ReDoc',
        redoc_js_url='static/redoc.standalone.js',
    )


@app.post('/v1/ideal-functions/select', tags=['Ideal Functions'])
async def select_ideal_functions() -> JSONResponse:
    """
    Initiates the ideal function selection process.

    Returns:
        JSONResponse: Status message and details of selected ideal functions.
    """
    try:
        ideal_function_manager.get_ideal_functions()
        selection_info = ideal_function_manager.ideal_functions_selection
        return JSONResponse(
            content={'message': 'Ideal function selection completed successfully.',
                     'selected_functions': selection_info},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ideal function selection failed: {e}')


@app.post('/v1/test-data/map', tags=['Test Data Mapping'])
async def map_test_data() -> JSONResponse:
    """
    Initiates the test data mapping process to ideal functions.

    Returns:
        JSONResponse: Status message and summary of the mapping results.
    """
    try:
        ideal_function_manager.map_test_data_to_ideal_functions()
        mapping_summary = f"{len(ideal_function_manager.results_db.read_data_from_table(table_name='TestDataMapping'))} test points mapped."
        return JSONResponse(
            content={'message': 'Test data mapping completed.',
                     'mapping_summary': mapping_summary},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Test data mapping failed: {e}')
    
@app.get('/v1/visualizations/all', tags=['Visualizations'], response_class=HTMLResponse)
async def get_all_data_visualization() -> HTMLResponse:
    """
    Serves the requested Bokeh visualization HTML file.
    
    Returns:
        FileResponse: The HTML file containing the Bokeh visualization.
    Raises:
        HTTPException: 404 if the visualization file is not found.
    """
    ideal_function_manager.get_all_functions_visualized()
    visualization_file_path = (
        Path.cwd() / 
        'data' / 
        dataset_name / 
        f'{VisualizationName.initial_data.value}.html'
    )
    try:
        with open(visualization_file_path) as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Visualization initial_data not found.')

@app.get('/v1/visualizations/{visualization_name}', tags=['Visualizations'], response_class=HTMLResponse)
async def get_visualization(visualization_name: VisualizationName) -> HTMLResponse:
    """
    Serves the requested Bokeh visualization HTML file.

    Args:
        visualization_name (VisualizationName): The names of the visualization files.

    Returns:
        FileResponse: The HTML file containing the Bokeh visualization.
    Raises:
        HTTPException: 404 if the visualization file is not found.
    """
    visualization_file_path = Path.cwd() / 'data' / dataset_name /  f'{visualization_name.value}.html'

    try:
        with open(visualization_file_path) as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f'Visualization {visualization_name} not found.')

@app.get('/v1/data/load-data', tags=['Data'])
async def load_data(dataset_type: DatasetType) -> JSONResponse:
    """
    Load the selected train, test or ideal data into DB for table view.

    Returns:
        JSONResponse: Status message.
    Raises:
        JSONResponse: 500 if there is an error loading data.
    """
    try:
        results_df = ideal_function_manager.data_manager.load_data(dataset_type=dataset_type) 
        if results_df.empty:
            return JSONResponse(content={'message': 'No data found.',}, status_code=404) 
        return JSONResponse(content={'message': 'Loaded data successfully.',}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error loading data into database: {e}')

@app.get('/v1/data/database-view', tags=['Data'])
async def get_database(dataset_type: DatasetType) -> HTMLResponse:
    """
    Retrieves the selected train, test or ideal data from DB for table view.

    Returns:
        HTMLResponse: Tableview of the selected data.
    Raises:
        HTTPException: 500 if there is an error retrieving data.
    """
    try:
        if dataset_type == DatasetType.TRAIN:
            table_name = 'TrainingData'
        elif dataset_type == DatasetType.IDEAL:
            table_name = 'IdealFunctions'
        elif dataset_type == DatasetType.TEST:
            table_name = 'TestData'

        results_df = ideal_function_manager.data_manager.read_data_from_table(table_name=table_name) 
        if results_df.empty:
            return HTMLResponse(content={'message': 'No data found.'}, status_code=200) 
        
        html_table = results_df.to_html(
        classes='styled-table',  # Add a CSS class named "styled-table"
        index=True,              # show index column
        na_rep='-',              # Represent NaN as hyphen
        )
        # Adopted from https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_html.html
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Pandas Table</title>
        <link rel="stylesheet" href="/static/table-template.css">  
        </head>
        <body>
        <h1>Database view with FastAPI: {table_name} </h1>
        {html_table}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error retrieving test mapping results from database: {e}')

@app.get('/v1/data/test-mapping-results', tags=['Data'])
async def get_test_mapping_results() -> HTMLResponse:
    """
    Retrieves the test data mapping results from the database.

    Returns:
        HTMLResponse: Tableview of mapping results.
    Raises:
        HTTPException: 500 if there is an error retrieving data.
    """
    try:
        results_df = ideal_function_manager.results_db.read_data_from_table(table_name='TestDataMapping') 
        if results_df.empty:
            return HTMLResponse(content={'message': 'No test data mappings found.'}, status_code=200) 
        
        html_table = results_df.to_html(
        classes='styled-table',  # Add a CSS class named "styled-table"
        index=True,              # show index column
        na_rep='-',              # Represent NaN as hyphen
        )
        # Adopted from https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_html.html
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Pandas Table</title>
        <link rel="stylesheet" href="/static/table-template.css">  
        </head>
        <body>
        <h1>Database view with FastAPI: Test Data Mapping</h1>
        {html_table}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error retrieving test mapping results from database: {e}')
