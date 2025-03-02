import logging
from pathlib import Path
import numpy as np
import pandas as pd
from src.application.DataManager import DataManager, DatasetType
from src.application.Visualizer import Visualizer, VisualizationName
from sklearn.linear_model import LinearRegression

class IdealFunctionsManager:
    """
    Manages a collection of ideal functions for mapping test data.
    """

    def __init__(self, dataset_name: str):
        """Initialize IdealFunctionsManager, setting up DataManager, Visualizer, and data structures."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('INFO')
        self.dataset_name = dataset_name
        self.data_manager: DataManager
        self.results_db: DataManager
        self.visualizer: Visualizer = Visualizer()
        self.ideal_functions_selection: dict = {}
        self.ideal_functions_data: pd.DataFrame = pd.DataFrame()
        self.training_data_max_deviations: dict = {}
        self.model = LinearRegression()
        self._init_databases()
        
        
    def _init_databases(self) -> None:
        """Creates one DB for train, test and ideal data and also one DB for results."""
        try:
            self.data_manager: DataManager = DataManager(self.dataset_name, database_name='data')
            self.results_db: DataManager = DataManager(self.dataset_name, 'results')
        except Exception as e:
            raise Exception(f'Error initializing DataManager: {e}') from e

    def _load_data(self, data_type: DatasetType) -> pd.DataFrame:
        """Loads and returns the specified dataset using DataManager with error handling.
        
        Args:
            data_type (DatasetType): Enum indicating the type of dataset to load.
        
        Returns:
            pd.DataFrame: Loaded dataset.
        
        """
        try:
            data = self.data_manager.load_data(dataset_type=data_type)
            if data.empty:
                raise ValueError(f'No data loaded for {data_type.value} dataset type.')
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f'Dataset file not found for {data_type.value} data.')
        except Exception as e:
            raise Exception(f'Error loading {data_type.value} data: {e}') from e


    def _calculate_squared_deviation(self, train_y: pd.Series, ideal_func_y: pd.Series, x: pd.Series) -> float:
        """
        Performs linear regression and calculates sum of squared deviations with error handling.
        
        Args:
            train_y (pd.Series): Series containing training data.
            ideal_func_y (pd.Series): Series containing ideal function data.
            x (pd.Series): Series containing x-values.
        
        Returns:
            float: Sum of squared deviations.

        """
        try:
            self.model.fit(x.values.reshape(-1, 1), ideal_func_y)
            y_predicted_ideal = self.model.predict(x.values.reshape(-1, 1))
            squared_deviations = (train_y - y_predicted_ideal)**2
            total_squared_deviation = squared_deviations.sum()
            return total_squared_deviation
        except Exception as e:
            raise Exception(f"Error calculating squared deviation: {e}") from e
        
    def get_all_functions_visualized(self) -> None:
        """Viusalizes test, train and ideal data in one plot.
        
        Returns:
            None
        
        """
        try:
            train_data = self._load_data(DatasetType.TRAIN)
            test_data = self._load_data(DatasetType.TEST)
            ideal_data = self._load_data(DatasetType.IDEAL)
        except Exception as e:
            self.logger.error(f'Data loading failed in : {e}')
            return

        # Create plot of Training and Ideal Data before selection
        try:
            self.visualizer.create_combined_plot(
                dataframes=[train_data, test_data, ideal_data],
                dataframe_names=['Training Data', 'Test Data', 'Ideal Functions'],
                x_col='x',
                y_cols=train_data.columns[1:].tolist() + test_data.columns[1:].tolist() + ideal_data.columns[1:].tolist(),
                title='Training Data , Test Data and All Ideal Functions',
                filename=Path.cwd() / 'data' / self.dataset_name / f'{VisualizationName.initial_data.value}.html',
            )
            self.logger.info(f'Initial data visualization saved to as {VisualizationName.initial_data.value}.html')
        except Exception as vizualisation_err:
            self.logger.warning(f'Initial data visualization failed: {vizualisation_err}')


    def get_ideal_functions(self) -> None:
        """
        Calculates best ideal functions, visualizes training and ideal data, and selected functions with error handling.
        
        Returns:
            None
        
        """
        try:
            train_data = self._load_data(DatasetType.TRAIN)
            ideal_data = self._load_data(DatasetType.IDEAL)
        except Exception as e:
            self.logger.error(f'Data loading failed in get_ideal_functions: {e}')
            return
        
        # Creates the initial visualization if not done beforehand
        self.get_all_functions_visualized()

        # Initialize variables
        best_ideal_functions_selection = {}
        ideal_functions_data_temp = []
        x_values = train_data['x']

        # Iterate each training data
        for train_col in train_data.columns[1:]:
            min_sum_squared_deviation = float('inf')
            best_ideal_func_name = None
            best_ideal_func_data = None
            # Iterate each ideal data
            for ideal_col in ideal_data.columns[1:]:
                try:
                    # Sum of all y-deviations squared
                    sum_squared_deviation = self._calculate_squared_deviation(train_data[train_col], ideal_data[ideal_col], x_values)
                except Exception as calc_err:
                    self.logger.warning(f'Squared deviation calculation failed for {train_col} and {ideal_col}: {calc_err}')
                    continue
                # Find smallest deviation of the sum
                if sum_squared_deviation < min_sum_squared_deviation:
                    min_sum_squared_deviation = sum_squared_deviation
                    best_ideal_func_name = ideal_col
                    best_ideal_func_data = ideal_data[ideal_col].copy()
            # Finally store best matches
            best_ideal_functions_selection[train_col] = best_ideal_func_name
            ideal_functions_data_temp.append(best_ideal_func_data)

            try:
                # Now find the best ideal functions match for the train data
                self.model.fit(x_values.values.reshape(-1, 1), ideal_data[best_ideal_func_name])
                y_predicted_ideal_for_train = self.model.predict(x_values.values.reshape(-1, 1))
                # Get max deviation out of column
                max_deviation_train = max(abs(train_data[train_col] - y_predicted_ideal_for_train))
                self.training_data_max_deviations[train_col] = max_deviation_train
            except Exception as model_error:
                self.logger.warning(f'Regression or deviation calculation failed for {train_col} and chosen {best_ideal_func_name}: {model_error}')
                self.training_data_max_deviations[train_col] = np.nan

        self.ideal_functions_selection = best_ideal_functions_selection
        # Get the keys and the corresponding dataframes together in desired structure
        self.ideal_functions_data = pd.DataFrame(dict(zip(best_ideal_functions_selection.keys(), ideal_functions_data_temp)))

        self.logger.info('Ideal functions selected for each training data column:')
        for train_col, ideal_col_name in self.ideal_functions_selection.items():
            self.logger.info(f'{train_col}: {ideal_col_name} (Max Training Deviation: {self.training_data_max_deviations[train_col]:.4f})')

        # Create Plot with Training Data with Selected Ideal Functions
        try:
            plot_dataframes = [train_data]
            plot_names = ['Training Data', 'Selected Ideal Functions']
            # Add selected ideal functions data
            plot_dataframes.append(pd.concat([x_values, self.ideal_functions_data], axis=1))

            self.visualizer.create_combined_plot(
                 dataframes=plot_dataframes,
                 dataframe_names=plot_names,
                 x_col='x',
                 y_cols=train_data.columns[1:].tolist() + self.ideal_functions_data.columns.tolist(),
                 title='Training Data with Selected Ideal Functions',
                 filename=Path.cwd() / 'data' / self.dataset_name / f'{VisualizationName.selected_ideal_functions.value}.html'
            )
            self.logger.info(f'Selected ideal functions visualization saved as {VisualizationName.selected_ideal_functions.value}.html')

        except Exception as vizualisation_err:
            self.logger.warning(f'Selected ideal functions visualization failed: {vizualisation_err}')


    def _store_results(self, results_to_save: pd.DataFrame) -> None:
        """Stores the results in the database using DataManager with error handling.
        
        Args:
            results_to_save (pd.DataFrame): DataFrame containing the results to be stored.
        """
        try:
            self.results_db.save_data(table_name='TestDataMapping', data=results_to_save)
        except Exception as e:
            self.logger.error(f'Error storing results to database: {e}')
            raise


    def map_test_data_to_ideal_functions(self) -> None:
        """Maps test data, visualizes mapping, and handles errors during mapping and saving."""
        try:
            test_data = self._load_data(DatasetType.TEST)
            ideal_data = self._load_data(DatasetType.IDEAL)
        except Exception as e:
            self.logger.error(f'Data loading failed in map_test_data_to_ideal_functions: {e}')
            return

        mapping_results = []
        # Iterate through each test data
        for _, test_row in test_data.iterrows():
            x_test = test_row['x']
            y_test = test_row['y']
            min_deviation_test_point = float('inf')
            
            best_ideal_func_name_for_test_point = None
            best_train_col_name_for_test_point = None
            # Iterate through each chosen ideal function
            for train_col_name, ideal_func_name in self.ideal_functions_selection.items():
                ideal_func_y_data = ideal_data[ideal_func_name]

                try:
                    x_ideal_for_regression = ideal_data['x']
                    self.model.fit(x_ideal_for_regression.values.reshape(-1, 1), ideal_func_y_data)
                    y_predicted_ideal_for_test_x = self.model.predict(np.array([[x_test]]))
                    deviation_test_point = abs(y_test - y_predicted_ideal_for_test_x[0])
                    max_train_deviation_for_func = self.training_data_max_deviations[train_col_name]
    	            # Now compare the deviation after the criterion (max_deviation * (2**0.5))
                    if deviation_test_point <= max_train_deviation_for_func * (2**0.5):
                        if deviation_test_point < min_deviation_test_point:
                            min_deviation_test_point = deviation_test_point
                            # Finally store data
                            best_ideal_func_name_for_test_point = ideal_func_name
                            best_train_col_name_for_test_point = train_col_name

                except Exception as mapping_error:
                    self.logger.warning(f'Mapping process error for test point x={x_test}, y={y_test} with ideal function {ideal_func_name}: {mapping_error}')
                    continue
            # Append each point to results
            if best_ideal_func_name_for_test_point:
                mapping_results.append({
                    'x': x_test,
                    'y': y_test,
                    'Delta Y': min_deviation_test_point,
                    'No. of ideal func': best_ideal_func_name_for_test_point,
                    'training_data_column': best_train_col_name_for_test_point
                })

        results_df = pd.DataFrame(mapping_results)
        try:
            # Drop the column to match with the desired table in the assignment
            self._store_results(results_df.drop('training_data_column', axis=1))
        except Exception as store_err:
            self.logger.warning(f'Error saving test data mapping results: {store_err}')

        self.logger.info(f'{len(results_df)} test points mapped to ideal functions.')
        if not results_df.empty:
            self.logger.info('First mappings:')
            self.logger.info(results_df.head())

            # Visualize Mapped Test Data
            try:
                # Load mapped test data from database for visualization
                mapped_test_data_from_db = self.results_db.read_data_from_table('TestDataMapping')

                plot_dataframes = [mapped_test_data_from_db]
                plot_names = ['Mapped Test Data', 'Corresponding Ideal Functions']

                # Add corresponding selected ideal functions for visualization context
                ideal_funcs_for_mapped_test = self.ideal_functions_data[results_df['training_data_column'].unique().tolist()]
                plot_dataframes.append(pd.concat([ideal_data['x'], ideal_funcs_for_mapped_test], axis=1).dropna(subset=['x']))

                self.visualizer.create_combined_plot(
                    dataframes=plot_dataframes,
                    dataframe_names=plot_names,
                    x_col='x',
                    y_cols=['y'] + ideal_funcs_for_mapped_test.columns.tolist(),
                    title='Mapped Test Data and Corresponding Ideal Functions',
                    filename=Path.cwd() / 'data' / self.dataset_name / f'{VisualizationName.mapped_test_data.value}.html')
                self.logger.info(f'Mapped test data visualization saved as {VisualizationName.mapped_test_data.value}.html')

            except Exception as vizualisation_err:
                self.logger.warning(f'Mapped test data visualization failed: {vizualisation_err}')

        else:
            self.logger.error('No test points could be mapped to ideal functions.')
