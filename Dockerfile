FROM python:3.8 as cleaner

# Add the files
ADD data.csv /tmp/data.csv
ADD scripts/cleanup.py /tmp/cleanup.py

# Run the code tests
RUN python -m unittest /tmp/cleanup.py

# Run the data cleanup and validation
RUN python /tmp/cleanup.py --enforcing \
    --infile=/tmp/data.csv --outfile=/tmp/clean.csv


FROM solr:8.11.0@sha256:f9f6eed52e186f8e8ca0d4b7eae1acdbb94ad382c4d84c8220d78e3020d746c6 as builder

USER root

# Set the SOLR_HOME directory env variable
ENV SOLR_HOME=/apps/solr/data

RUN mkdir -p /apps/solr/ && \
    cp -r /opt/solr/server/solr /apps/solr/data && \
    wget --directory-prefix=/apps/solr/data/lib "https://maven.lib.umd.edu/nexus/repository/releases/edu/umd/lib/umd-solr/2.2.2-2.4/umd-solr-2.2.2-2.4.jar" && \
    wget --directory-prefix=/apps/solr/data/lib "https://maven.lib.umd.edu/nexus/repository/central/joda-time/joda-time/2.2/joda-time-2.2.jar" && \
    chown -R solr:0 "$SOLR_HOME"

# Switch back to solr user
USER solr

COPY --from=cleaner /tmp/clean.csv /tmp/clean.csv

# Create the "scpa-scores" core
RUN /opt/solr/bin/solr start && \
    /opt/solr/bin/solr create_core -c scpa-scores && \
    /opt/solr/bin/solr stop

# Replace the schema file
COPY conf /apps/solr/data/scpa-scores/conf/

# Load the data to scpa-scores core
RUN /opt/solr/bin/solr start && \
    sleep 3 && \
    curl --verbose \
       "http://localhost:8983/solr/scpa-scores/update" \
       --data-binary @/tmp/clean.csv \
       --header 'Content-type:text/csv; charset=utf-8' && \
    /opt/solr/bin/solr stop


FROM solr:8.11.0-slim@sha256:530547ad87f3fb02ed9fbbdbf40c0bfbfd8a0b472d8fea5920a87ec65aaacaef

ENV SOLR_HOME=/apps/solr/data

USER root
RUN mkdir -p /apps/solr/

USER solr
COPY --from=builder /apps/solr/ /apps/solr/
