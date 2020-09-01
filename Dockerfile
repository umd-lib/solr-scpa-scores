FROM python:3.8 as cleaner

# Add the data to be loaded
ADD data.csv /tmp/data.csv

# Add and run cleanup.py
ADD scripts/cleanup.py /tmp/cleanup.py
RUN cd /tmp && python cleanup.py data.csv clean.csv


FROM solr:8.1.1 as builder

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


FROM solr:8.1.1-slim

ENV SOLR_HOME=/apps/solr/data

USER root
RUN mkdir -p /apps/solr/

USER solr
COPY --from=builder /apps/solr/ /apps/solr/
