# aind-analysis-job-dispatch

This repository contains a **job dispatcher** that creates standardized analysis dispatch models for large-scale data analysis workflows. It's designed to query a metadata database, locate relevant data assets in cloud storage, and prepare them for parallel processing by analysis workers.

## What it does

The job dispatcher:
1. **Queries** a metadata database to find datasets matching your criteria
2. **Locates** the corresponding data files in S3 cloud storage
3. **Creates** standardized analysis dispatch models containing file locations and metadata
4. **Distributes** these jobs across multiple parallel workers for efficient processing

## Key Concepts

- **Analysis Dispatch Model**: A standardized JSON structure (`AnalysisDispatchModel`) that contains all the information needed to process a dataset, including S3 file locations, asset IDs, and analysis parameters.

- **Data Asset**: A collection of related files (e.g., experimental recordings, processed data) stored in cloud storage with associated metadata.

- **Document Database Query**: A MongoDB-style filter that specifies which datasets to include in your analysis (e.g., `{"subject.subject_id": "774659", "data_description.process_name": "processed"}`).

- **Parallel Workers**: Independent processing units that each handle a subset of the total jobs, enabling large-scale analysis.

- **Distributed Parameters**: Analysis parameters to apply for each data asset.

## Installation and Setup

This is a [Code Ocean](https://codeocean.allenneuraldynamics.org/capsule/9303168/tree) capsule. To use it:

1. **Access the capsule** at the link above
2. **Configure your query** using the app panel or by providing input files
3. **Configure your analysis parameters** by providing the json parameters to apply to each asset
3. **Run the capsule** to generate analysis dispatch models
4. **Use the output** with downstream analysis workflows

## Usage


### Input Methods

You have two ways to specify which data assets to process:

#### Method 1: Database Query (Recommended)
Provide a MongoDB-style query to filter datasets:

**Examples:**
- Simple query: `{"subject.subject_id": "774659"}`
- Complex query: `{"data_description.project_name": "Ephys Platform", "subject.subject_id": {"$in": ["643634", "774659"]}}`
- Query from file: Provide the path to a JSON file containing your query

**Using the Query Generator:**
Use the [metadata query portal](https://metadata-portal.allenneuraldynamics.org/query) to build queries interactively (currently in development). You can also use [GAMER](https://metadata-chatbot-dev.streamlit.app/) to generate interactive queries.

#### Method 2: Asset ID List
Provide a CSV file with specific data asset IDs:

1. Set `--use_data_asset_csv=1`
2. Include a CSV file in the `/data` folder named `data_asset_input.csv`
3. The CSV must have a column named `asset_id` with the data asset IDs

### File Processing Options

- **File Extension Filtering**: Use `--file_extension` to only process specific file types (e.g., `.nwb`, `.zarr`)
- **File Grouping**: 
  - `--split_files=1`: Create separate jobs for each file (default)
  - `--split_files=0`: Group all files from the same asset into one job


## Output

### Analysis Dispatch Models

The dispatcher creates **analysis dispatch models** that conform to the [`AnalysisDispatchModel`](https://github.com/AllenNeuralDynamics/analysis-pipeline-utils/blob/main/src/analysis_pipeline_utils/analysis_dispatch_model.py) schema. 

### File Structure

For parallelization, the output creates:
- **One folder per worker** (0, 1, 2, ... up to `num_parallel_workers`)
- **One JSON file per job** within each worker folder
- **Unique UUID filenames** for each job

### Analysis Dispatch Model Content

Each analysis dispatch model is a JSON file containing:

```json
{
    "s3_location": [
        "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/50fa9416-4e21-482f-8901-889322a87ae3"
    ],
    "file_location": [
        "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/50fa9416-4e21-482f-8901-889322a87ae3/nwb/behavior_774659_2025-06-07_14-31-15.nwb"
    ],
    "distributed_parameters": [
        {
            "param_name": "foo",
            "param_value": 10,
            "version": 1.0
        }
    ]
}
```

**Field Descriptions:**
- `s3_location`: Base S3 bucket path(s) containing the data asset
- `file_location`: Specific file path(s) when using file extension filtering
- `distributed_parameters`: Partial parameter sets from the `analysis_parameters.json` file to run on each data asset


## Integration with Analysis Workflows

This job dispatcher is typically used as the first step in a larger analysis pipeline:

1. **Job Dispatch** (this repository) → Creates analysis dispatch models
2. **Analysis Wrapper** → Processes each job using the input models  

See the [aind-analysis-pipeline-template](https://github.com/AllenNeuralDynamics/aind-analysis-pipeline-template) for a complete workflow example.

## Development

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd aind-analysis-job-dispatch/code

# Install dependencies
pip install -e .[dev]

# Run tests
python -m unittest discover tests/
```

### Code Structure

- `run_capsule.py`: Main entry point and orchestration logic
- `utils.py`: Database queries and S3 operations
- `tests/`: Unit tests for key functionality

## Troubleshooting

**No files found**: Ensure your file extension is correct and files exist in the S3 locations
**Query returns no results**: Verify your database query syntax and field names
**Permission errors**: Check that AWS credentials are properly configured

## Advanced Features

### Analysis Parameters

You can specify analysis parameters by including an `analysis_parameters.json` file in the `/data/analysis_parameters/` folder. This file contains two keys:

- **`fixed_parameters`**: A single dictionary following your analysis input schema. Use this when you want to run the same analysis parameters on all data assets (N assets → N jobs).

- **`distributed_parameters`**: A list of dictionaries, each following your analysis input schema. Use this when you want to run multiple different analyses (N assets × M parameter sets → N×M jobs). 

**Example:**
```json
{
    "fixed_parameters": {
        "analysis_name": "Unit Quality Filtering",
        "analysis_tag": "baseline_v1.0",
        "isi_violations_cutoff": 0.05,
    },
    "distributed_parameters": [
        {
            "method": "isolation_distance"
        },
        {
            "method": "amplitude_cutoff"
        }
    ]
}
```


The analysis wrapper capsule merges these, together with any commond-line or app-panel inputs, and the final merged parameter set should follow the analysis input schema specified in that capsule.


## Additional Resources


### Related Repositories
- [aind-analysis-wrapper](https://github.com/AllenNeuralDynamics/aind-analysis-wrapper): Processes the analysis dispatch models created by this dispatcher
- [aind-analysis-pipeline-template](https://github.com/AllenNeuralDynamics/aind-analysis-pipeline-template): Complete pipeline template combining dispatcher and wrapper


