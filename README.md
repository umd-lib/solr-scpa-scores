# solr-scpa-scores

## Introduction

Note: Previous versions of this repository were used as a Solr configuration
directory on solr.lib.umd.edu. This repository has now been changed to support
creating a Docker image containing the data.

When making updates to the data or configuration, a new Docker image should be
created.

---

## Important Note

The "data.csv" file included in this branch was generated by exporting data
from the existing solr.lib.umd.edu instance, and corresponds to the
"scpa-scores-solr_20191106.csv" file from
[Confluence](https://confluence.umd.edu/display/LIB/SolrDB+Project%3A+SCPA+Scores+Collection).

This version of the repository does _not_ support CSV files provided by SCPA.
See the "scpa_csv_import" branch for a version that can be used as a base
for processing CSV files provided by SCPA.

---

## Building the Docker Image

When building the Docker image, the "data.csv" file will be used to populate
the Solr database.

To build the Docker image named "solr-scpa-scores":

```
> docker build -t solr-scpa-scores .
```

To run the freshly built Docker container on port 8983:

```
> docker run -it --rm -p 8983:8983 solr-scpa-scores
```

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
