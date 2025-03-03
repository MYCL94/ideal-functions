**Project Title:** Ideal Function Mapping and Visualization with FastAPI and Bokeh


**Project Description:**

The goal of this project is to develop a Python-based application that can load training data, identify the best ideal functions, map test data points to these ideal functions, and visualize the results. The project involves several key components:

1. **Data Loading**: Load training data from a CSV file into a SQLite database using SQLAlchemy.
2. **Ideal Function Selection**: Identify the four ideal functions that best fit the training data using the least-squares method.
3. **Test Data Mapping**: Map each test data point to one of the chosen ideal functions based on maximum deviation criterion.
4. **Visualization**: Create plots for the training data, test data, and mapped test data using Bokeh.


## Getting Started

> requires python 3.11

```
# Setup
$ git clone git@bitbucket.org:MYCL94/ideal-functions.git
$ cd ideal-functions

$ python -m venv ./venv
$ cd .venv/Scripts
$ activate.bat
$ (uv) pip install -r pyproject.toml
$ python -m src.ideal_functions_application

```

> Check `curl localhost:8080/`

## Available APIs

**Data Analysis**

`/v1/ideal-functions/select`

`/v1/test-data/map`

**Visualizations**

`/v1/visualizations/all`

`/v1/visualizations/{visualization_name}`

**Data**

`/v1/data/load-data`

`/v1/data/database-view`

`/v1/data/test-mapping-results`


## Preparing Additional Data

If you need to test with custom data, follow these steps:

1. Copy new data: Place your custom data files in the /data folder.
2. Specify dataset name: Set an environment variable named **DATASET_NAME** to the name of the directory containing your new data.

**Environment Variable Priority**

Note that if you've set a value for **DATASET_NAME**, the application will use it instead of looking for a default dataset. This allows you to easily switch between different datasets during testing or development.

## Testing

Collect all the tests with 
`python -m pytest --collect-only`

Run the tests with
`python -m pytest`

## Git Version Control

**Clone the Project:**

Use the following Git command to clone the 'develop' branch of the project to your local machine:

```
git clone -b develop https://github.com/MYCL94/ideal-functions.git
```

**Make Changes:**

Add a New Feature or fix a bug:
Make the necessary code changes to add your new function.
Use the following Git commands to commit and push your changes to the 'develop' branch:

```
$ git add.
$ git commit -m "New-function"
$ git push origin develop 
```

**Create a Pull Request:**
After pushing your changes, create a pull request on Github to merge your changes into the main 'develop' branch.    
Project members will review your code, and once approved, your changes will be merged.    
