# aind-analysis-job-dispatch

This capsule will create the job input model for the analysis workflow. Required parameters and steps are below. Capsule link: https://codeocean.allenneuraldynamics.org/capsule/9303168/tree

### Usage
This script accepts several command-line arguments:

| Argument               | Type    | Description                                                                                                                                             |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--query`  | string | The dictionary filter to query the document database.
| `--file_extension`      | string  | The file extension to search for from the bucket returned by the query. Defualt is empty                                                                                                             |
| `--split_files`   | int  | Either group the files into one list if multiple files are returned for the file extension or split into single input per file. Default is to split
| `--num_parallel_workers`    | int  |  The number of parallel workers to output, default is 50
| `--use_data_assets`  | int | Whether or not to use the data asset ids in the csv provided. Default is 0. If 1, there MUST be a csv in the `/data` folder called `data_asset_input.csv`, with the column `asset_id`.

### Example Command:

```bash
python script.py \
    --query '{"name": {"$regex": "^behavior_741213.*processed"}}'
    --file_extension "" \
    --split_files 1 \
    --num_parallel_workers 50
```

### Specifying Analysis Specification
The analysis specification can be provided like so: A json file with a list of dictionaries following `AnalysisSpecification` model defined in `job_dispatch.analysis_input_model.py`. An example is below:
```json
[
    {
        
        "analysis_name": "Unit Yield",
        "analysis_version": "v0.0.5",
        "analysis_libraries": [
            "aind-ephys-utils"
        ],
        "analysis_parameters": {
            "isi_violations": 0.5
        },
        "s3_output_bucket": "aind-scratch-data/arjun.sridhar"
    },

    {
        
        "analysis_name": "Unit Filtering",
        "analysis_version": "v0.0.5",
        "analysis_libraries": [
            "aind-ephys-utils"
        ],
        "analysis_parameters": {
            "isi_violations": 0.5, "amplitude_cutoff": 0.1
        },
        "s3_output_bucket": "aind-scratch-data/arjun.sridhar"
    }
]
```

### Example Output File Content

For parallelization, the output will be a folder for each worker. The output will be a json with a uuid as the filename. Example content shown below.

```json
{

    "s3_location": "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/d94ab360-f393-41f4-831f-e098f11803df",
    "location_asset_id": "d94ab360-f393-41f4-831f-e098f11803df",
    "file_extension_locations": null,
    "asset_name": "behavior_741213_2024-08-26_16-28-28_processed_2024-09-17_07-25-04"

}
```

```


### Metadata Query Generator (In development)
The linked portal helps generate simple queries that can be used as input into the job dispatch. Currently under development, but example query from filling out fields: `{"data_description.project_name": "Ephys Platform", "subject.subject_id": {"$in": ["643634"]}}`.
Portal link: https://metadata-portal.allenneuraldynamics.org/query


