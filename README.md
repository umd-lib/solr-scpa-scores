# solr-scpa-scores

## Introduction

Note: Previous versions of this repository were used as a Solr configuration
directory on solr.lib.umd.edu. This repository has now been changed to support
creating a Docker image containing the data.

When making updates to the data or configuration, a new Docker image should be
created.

## Building the Docker Image

When building the Docker image, the "data.csv" file will be used to populate
the Solr database.

To build the Docker image named "solr-scpa-scores":

``` bash
> docker build -t solr-scpa-scores .
```

To run the freshly built Docker container on port 8983:

``` bash
> docker run -it --rm -p 8983:8983 solr-scpa-scores
```

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
