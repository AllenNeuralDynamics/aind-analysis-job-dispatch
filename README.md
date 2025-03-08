# aind-analysis-job-dispatch

This capsule will create the job input model for the analysis workflow. Currently, this only looks for nwb files for first order analysis. Required parameters and steps are below. Capsule link: https://codeocean.allenneuraldynamics.org/capsule/9303168/tree

### Usage
This script accepts several command-line arguments:

| Argument               | Type    | Description                                                                                                                                             |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--query`              | string  | A JSON string representing the query to retrieve the S3 file locations. The nwb file for the query will be searched for.                                                                                |
| `--analysis_name`      | string  | The name of the analysis function to be run.                                                                                                             |
| `--analysis_version`   | string  | The version of the analysis function to run.                                                                                                            |
| `--analysis_libraries` | string  | A JSON string representing a list of analysis libraries that will be used (e.g., `["library1", "library2"]`).                                            |
| `--analysis_parameters`| string  | A JSON string representing the analysis parameters (e.g., `{"param1": "value1", "param2": "value2"}`).                                                    |

### Example Command:

```bash
python script.py \
    --query '{"name": "experiment_12345"}' \
    --analysis_name "Unit_Yield" \
    --analysis_version "0.1.0" \
    --analysis_libraries '["aind-ephys-utils"]' \
    --analysis_parameters '{"alpha": "0.1"}'
```

### Example Output File Content

The content of the JSON file will look something like this (it will be saved as `file1_Unit_Yield_0.1.0.json`):

```json
{
  "s3_location": "s3://bucket/path/to/file1.nwb",
  "analysis_spec": {
    "analysis_name": "Unit Yield",
    "analysis_version": "0.1.0",
    "analysis_libraries_to_track": ["aind-ephys-utils"],
    "analysis_parameters": {"alpha": "0.1"}
  }
}


