from enum import Enum
import logging
from pathlib import Path
from bokeh.plotting import figure, save, output_file
from bokeh.models import Legend, ColumnDataSource
from bokeh.palettes import Category20
import pandas as pd

class VisualizationName(Enum):
    """Enumeration of visualization names."""
    initial_data = 'initial_data'
    selected_ideal_functions = 'selected_ideal_functions'
    mapped_test_data = 'mapped_test_data'

class Visualizer:
    """
    Provides data visualization capabilities using Bokeh.
    Enhanced with responsive plot sizing.

    Methods:
        _configure_legend_layout(legend: Legend, plot: figure) -> None
        _save_plot(plot: figure, filename:str | Path) -> None
        create_combined_plot(...) -> None
    """
    def __init__(self,) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('INFO')

    def _configure_legend_layout(self, legend: Legend, plot: figure) -> None:
        """
        Configures the layout and style of the legend and adds it to the plot.

        Args:
            legend (Legend): The Bokeh Legend object.
            plot (figure): The Bokeh figure to add the legend to.
        """
        plot.add_layout(legend, 'right')
        legend.orientation = 'vertical'
        legend.ncols = 2
        legend.click_policy = 'hide'
        legend.label_text_font_size = '12px'
        self.logger.info('Legend configured and added to plot.')

    def _save_plot(self, plot: figure, filename:str | Path) -> None:
        """Saves the plot to Dataset specific folder (created if not existing).
        
        Args:
            plot (figure): The Bokeh figure to save.
            filename (str or Path): The name of the file.
        """

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        output_file(filename, title='Visualizer Plot')
        save(plot, filename=filename, title='Visualizer Plot')
        self.logger.info(f'Plot saved to {filename}')

    def create_combined_plot(self, 
                             dataframes:list[pd.DataFrame], 
                             dataframe_names:list, x_col:str,
                             y_cols:list[str], 
                             title:str='Combined Data Plot', 
                             filename:str | Path='combined_plot.html') -> None:
        """
        Creates a combined Bokeh scatter plot from multiple DataFrames with responsive sizing.

        Args:
            dataframes (list): A list of pandas DataFrames to be plotted.
            dataframe_names (list): A list of names corresponding to the DataFrames.
            x_col (str): The column name for the x-axis.
            y_cols (list): A list of column names for the y-axis.
            title (str): The title of the plot.
            filename (str or Path): The name of the output HTML file.
        """
        
        plot = figure(title=title, x_axis_label=x_col, y_axis_label='Y Values',
                      sizing_mode='stretch_both',
                      width=1000, height=800)

        items = []
        default_colors = Category20[20]
        color_index = 0
        # Iterate through each dataframe
        for i, df in enumerate(dataframes):
            df_name = dataframe_names[i]

            y_cols_for_df = []

            for df_col_name in df.columns[1:]:
                if df_col_name in y_cols:
                    y_cols_for_df.append(df_col_name)

            # Add each source and change color per plot
            for y_col in y_cols_for_df:
                source = ColumnDataSource(df)
                color = default_colors[color_index % len(default_colors)]
                glyph = plot.scatter(x=x_col, y=y_col, source=source, color=color, size=5, alpha=0.6)
                items.append((f"{df_name} - {y_col}", [glyph]))
                color_index += 1

        # Add a legend
        legend = Legend(items=items)
        self._configure_legend_layout(legend, plot)
        # Save the plot to as HTML
        self._save_plot(plot, filename)