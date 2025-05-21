# aind-analysis-job-dispatch

This capsule will create the job input model for the analysis workflow. Required parameters and steps are below. Capsule link: https://codeocean.allenneuraldynamics.org/capsule/9303168/tree

### Usage
This script accepts several command-line arguments:

| Argument               | Type    | Description                                                                                                                                             |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--file_extension`      | string  | The file extension to search for from the bucket returned by the query. Defualt is empty                                                                                                             |
| `--split_files`   | int  | Either group the files into one list if multiple files are returned for the file extension or split into single input per file. Default is to split
| `--num_parallel_workers`    | int  |  The number of parallel workers to output, default is 50

### Example Command:

```bash
python script.py \
    --file_extension "" \
    --split_files 1 \
    --num_parallel_workers 50
```

### Specifying Necessary Contents
There are 2 required user defined variables that need to be set in the code. They are both found in `code/job_dispatch/run_capsule.py`. The first of these is either the query or list of data assets. Look in the main section of `run_capsule.py` and replace with desired query or list of data assets to get input model.

The last necessary thing is to define the input analysis specification. This is in the function `get_analysis_specifications()` in `run_capsule.py`. Navigate to this function and create your desired analysis specifications and append to the list. The output of the dispatcher will be a json for every analysis-input-data combination. See example content below.

### Example Output File Content

The content of the JSON file will look something like this (it will be saved as bucket_name.json):

```json
{
    "s3_location": "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/d94ab360-f393-41f4-831f-e098f11803df",
    "location_asset_id": "d94ab360-f393-41f4-831f-e098f11803df",
    "location_uri": null,
    "asset_name": "behavior_741213_2024-08-26_16-28-28_processed_2024-09-17_07-25-04",
    "parameters": {
        "analysis_name": "Unit Yield",
        "analysis_version": "v0.0.1",
        "analysis_libraries_to_track": [
            "aind-ephys-utils"
        ],
        "analysis_parameters": {
            "isi_violations": 0.5
        }
    }
}
```

### Metadata Query Generator (In development)
The linked portal helps generate simple queries that can be used as input into the job dispatch. Currently under development, but example query from filling out fields: `{"data_description.project_name": "Ephys Platform", "subject.subject_id": {"$in": ["643634"]}}`.
Portal link: https://metadata-portal.allenneuraldynamics.org/query


