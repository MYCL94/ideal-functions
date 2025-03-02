import shutil
import pytest
from pathlib import Path
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Legend
from src.application.Visualizer import Visualizer

TEST_DATA_DIR = Path('./test/temp')

@pytest.fixture(scope='module')
def visualizer():
    """Fixture to create a Visualizer instance."""
    
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    yield Visualizer()

    shutil.rmtree(str(TEST_DATA_DIR.absolute()), ignore_errors=True)


@pytest.fixture(scope='module')
def sample_data():
    """Fixture to create a sample DataFrame."""
    data = {'x': [1, 2, 3, 4, 5],
            'y1': [2, 4, 1, 3, 5],
            'y2': [3, 1, 4, 2, 6],
            'y3': [3,2,5,4,3]}
    return pd.DataFrame(data)


def test_configure_legend_layout(visualizer:Visualizer):
    """Test the configure_legend_layout method."""
    plot = figure()
    legend = Legend()
    visualizer._configure_legend_layout(legend, plot)

    assert legend.orientation == 'vertical'
    assert legend.ncols == 2
    assert legend.click_policy == 'hide'
    assert legend.label_text_font_size == '12px'


def test_save_plot(visualizer:Visualizer):
    """Test the save_plot method."""
    plot = figure()
    test_filename = TEST_DATA_DIR / 'test_plot.html'
    visualizer._save_plot(plot, test_filename)

    assert test_filename.exists()
    test_filename.unlink()


def test_create_combined_plot(visualizer:Visualizer, sample_data):
    """Test the create_combined_plot method."""
    test_filename = TEST_DATA_DIR / 'test_combined_plot.html'
    visualizer.create_combined_plot(
        dataframes=[sample_data, sample_data],
        dataframe_names=['Data1', 'Data2'],
        x_col='x',
        y_cols=['y1','y2','y3'],
        title='Test Combined Plot',
        filename=test_filename
    )

    assert test_filename.exists()
    test_filename.unlink()
    
def test_create_combined_plot_with_missing_y_columns(visualizer:Visualizer, sample_data):
    """Test create_combined_plot when some specified y_cols are not in the DataFrames."""
    test_filename = TEST_DATA_DIR / 'test_combined_plot_missing_y.html'
    visualizer.create_combined_plot(
        dataframes=[sample_data],
        dataframe_names=['Data1'],
        x_col='x',
        y_cols=['y1', 'y_missing'],
        title='Test Combined Plot with Missing Y Columns',
        filename=test_filename
    )

    assert test_filename.exists()
    test_filename.unlink()

def test_create_combined_plot_empty_dataframes(visualizer:Visualizer):
    """Test create_combined_plot with empty dataframe."""
    test_filename = TEST_DATA_DIR / 'test_combined_plot_empty.html'
    visualizer.create_combined_plot(
        dataframes=[],
        dataframe_names=[],
        x_col='x',
        y_cols=['y1','y2'],
        title='Test Combined Plot with Missing Y Columns',
        filename=test_filename
    )

    assert test_filename.exists()
    test_filename.unlink()
