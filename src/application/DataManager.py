import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, exc
from enum import Enum

from src.application.CustomError import CustomError

class DatasetType(Enum):
    TRAIN = 'train'
    TEST = 'test'
    IDEAL = 'ideal'

class DataManager:
    """
    Manages loading data from CSV files into a SQLite database and saving DataFrames to the database.

    Attributes:
        dataset_name (str): The name of the dataset to load.
        database_name (str): The base name of the SQLite database file (without extension).

    Methods:
        _create_databases() -> None: Creates and validates the database connection.
        load_data(dataset_type: DatasetType) -> pd.DataFrame: Loads data from a CSV file into a DataFrame and the corresponding SQLite table).
        read_data_from_table(table_name: str) -> pd.DataFrame: Reads data from a specified SQLite table into a DataFrame        
        save_data(table_name: str, data: pd.DataFrame) -> None: Saves a DataFrame to a specified SQLite table.
    """

    def __init__(self, dataset_name: str, database_name: str):
        """
        Initializes DataManager with the specified database name.

        Args:
            dataset_name (str): The name of the dataset to load.
            database_name (str): The base name for the SQLite database file (e.g., 'my_dataset').
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('INFO')
        self.dataset_name = dataset_name
        self.database_name = database_name
        self._create_databases()

    def _create_databases(self) -> None:
        """
        Creates and validates the database connection.

        Raises:
            Exception: If the database connection fails.
        """
        db_path = Path.cwd() / 'data' / self.dataset_name / f'{self.database_name}.sqlite'
        try:
            self.engine = create_engine(f'sqlite:///{db_path}')
            with self.engine.connect():
                self.logger.info(f'Test connection to database: {db_path} successful.')
        except exc.SQLAlchemyError as e:
            raise CustomError(f'Failed to connect to database: {db_path}. Error: {e}') from e

    def load_data(self, dataset_type: DatasetType) -> pd.DataFrame:
        """
        Loads data from a CSV file into a Pandas DataFrame and a SQLite database table.

        CSV files are expected in the 'data/{database_name}/' directory, named as '{dataset_type.value}.csv' (e.g., data/my_dataset/train.csv).
        Loads data into tables named "TrainingData", "IdealFunctions", or a table named after dataset_type if it's not TRAIN or IDEAL.

        Args:
            dataset_type (DatasetType):  Enum indicating the type of dataset to load (TRAIN, TEST, IDEAL).

        Returns:
            pd.DataFrame: A pandas DataFrame containing the loaded data.

        Raises:
            FileNotFoundError: If the CSV file is not found.
            pd.errors.ParserError: If there's an error parsing the CSV file.
            Exception: For other database related errors.
        """
        file_path = Path.cwd() / 'data' / self.dataset_name / f'{dataset_type.value}.csv'
        table_name = ''

        if dataset_type == DatasetType.TRAIN:
            table_name = 'TrainingData'
        elif dataset_type == DatasetType.IDEAL:
            table_name = 'IdealFunctions'
        elif dataset_type == DatasetType.TEST:
            table_name = 'TestData'

        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            return df
        except FileNotFoundError as e:
            raise FileNotFoundError(f'CSV file not found: {file_path}. Error: {e}') from e
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f'Error parsing CSV file: {file_path}. Error: {e}') from e
        except exc.SQLAlchemyError as e:
            raise CustomError(f'Database error while loading data to table {table_name}: {e}') from e


    def read_data_from_table(self, table_name: str) -> pd.DataFrame:
        """
        Reads data from a specified SQLite database table into a Pandas DataFrame.

        Args:
            table_name (str): The name of the database table to read from (e.g., "TestDataMapping").

        Returns:
            pd.DataFrame: A pandas DataFrame containing the data read from the table.

        Raises:
            Exception: If there is an error during database reading, such as table not found or other SQL errors.
        """
        try:
            sql_query = f'SELECT * FROM `{table_name}`'
            df = pd.read_sql_query(sql_query, self.engine)
            return df
        except exc.SQLAlchemyError as e:
            raise CustomError(f'Database error while reading data from table {table_name}: {e}') from e

    
    def save_data(self, table_name: str, data: pd.DataFrame) -> None:
        """
        Saves a DataFrame to a specified SQLite database table. Replaces if the table already exists.

        Args:
            table_name (str): The name of the database table where data will be saved (e.g., "TestDataMapping").
            data (pd.DataFrame): The DataFrame containing the data to be saved.

        Raises:
            Exception: If there is an error during database saving.
        """
        try:
            data.to_sql(table_name, self.engine, if_exists='replace', index=False)
        except exc.SQLAlchemyError as e:
            raise CustomError(f'Database error while saving data to table {table_name}: {e}') from e