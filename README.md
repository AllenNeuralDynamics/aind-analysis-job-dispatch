# aind-analysis-job-dispatch

This capsule will create the job input model for the analysis workflow. Required parameters and steps are below. Capsule link: https://codeocean.allenneuraldynamics.org/capsule/9303168/tree

### Usage
This script accepts several command-line arguments:

| Argument               | Type    | Description                                                                                                                                             |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--query`  | string | The dictionary filter to query the document database or the path to a json containing the query.
| `--file_extension`      | string  | The file extension to search for from the bucket returned by the query. Defualt is empty                                                                                                             |
| `--split_files`   | int  | Either group the files into one list if multiple files are returned for the file extension or split into single input per file. Default is to split
| `--max_jobs`    | int  |  The number of parallel workers to output, default is 50
| `--use_data_asset_csv`  | int | Whether or not to use the data asset ids in the csv provided. Default is 0. If 1, there MUST be a csv in the `/data` folder called `data_asset_input.csv`, with the column `asset_id`.


If you want to group the data assets into certain groupings, see portion of code in `run_capsule` in line 216 where you can specify the grouping you desire.

### Example Output File Content

For parallelization, the output will be a folder for each worker. The output will be a json model (model lives here [Dispatch Analysis Model](https://github.com/AllenNeuralDynamics/aind-analysis-results/blob/main/src/aind_analysis_results/analysis_dispatch_model.py) with a uuid as the filename. Example content shown below.

```json
{
    "s3_location": [
        "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/50fa9416-4e21-482f-8901-889322a87ae3"
    ],
    "asset_id": [
        "50fa9416-4e21-482f-8901-889322a87ae3"
    ],
    "asset_name": [
        "behavior_774659_2025-06-07_14-31-15_processed_2025-06-08_03-49-49"
    ],
    "file_location": [
        "s3://codeocean-s3datasetsbucket-1u41qdg42ur9/50fa9416-4e21-482f-8901-889322a87ae3/nwb/behavior_774659_2025-06-07_14-31-15.nwb"
    ]
}
```

```


### Metadata Query Generator (In development)
The linked portal helps generate simple queries that can be used as input into the job dispatch. Currently under development, but example query from filling out fields: `{"data_description.project_name": "Ephys Platform", "subject.subject_id": {"$in": ["643634"]}}`.
Portal link: https://metadata-portal.allenneuraldynamics.org/query


