# aind-analysis-job-dispatch

This capsule will create the job input model for the analysis workflow. Required parameters and steps are below. Capsule link: https://codeocean.allenneuraldynamics.org/capsule/9303168/tree

### Usage
This script accepts several command-line arguments:

| Argument               | Type    | Description                                                                                                                                             |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--query`              | string  | A JSON string representing the query to retrieve the S3 bucket                                                                              |
| `--file_extension`      | string  | The file extension to search for from the bucket returned by the query. Defualt is empty                                                                                                             |
| `--split_files`   | string  | Either group the files into one list if multiple files are returned for the file extension or split into single input per file. Default is to split                                                                                            

### Example Command:

```bash
python script.py \
    --query '{"name": "experiment_12345"}' \
    --file_extension "nwb" \
    --split_files 1 \
```

### Example Output File Content

The content of the JSON file will look something like this (it will be saved as bucket_name.json):

```json
{
    "location_bucket": "s3://path/to/bucket123",
    "location_asset_id": "bucket123",
    "location_uri": "s3://path/to/bucket123/file.nwb"
}
```

### Metadata Query Generator (In development)
The linked portal helps generate simple queries that can be used as input into the job dispatch. Currently under development, but example query from filling out fields: `{"data_description.project_name": "Ephys Platform", "subject.subject_id": {"$in": ["643634"]}}`.
Portal link: https://metadata-portal.allenneuraldynamics.org/query


