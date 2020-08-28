FROM solr:8.1.1 as builder

# Switch to root user
USER root

# Install xmlstarlet and Python
# (dos2unix, Python, and csvkit are used by scripts/cleanup.sh)
RUN apt-get update -y && \
    apt-get install -y xmlstarlet && \
    apt-get install -y dos2unix && \
    apt-get install -y python3-dev python-dev python-pip python-setuptools build-essential && \
    pip install csvkit

# Set the SOLR_HOME directory env variable
ENV SOLR_HOME=/apps/solr/data

RUN mkdir -p /apps/solr/ && \
    cp -r /opt/solr/server/solr /apps/solr/data && \
    wget --directory-prefix=/apps/solr/data/lib "https://maven.lib.umd.edu/nexus/repository/releases/edu/umd/lib/umd-solr/2.2.2-2.4/umd-solr-2.2.2-2.4.jar" && \
    wget --directory-prefix=/apps/solr/data/lib "https://maven.lib.umd.edu/nexus/repository/central/joda-time/joda-time/2.2/joda-time-2.2.jar" && \
    chown -R solr:0 "$SOLR_HOME"

# Add the data to be loaded
ADD data.csv /tmp/data.csv

# Add and run cleanup.sh
ADD scripts/cleanup.sh /tmp/cleanup.sh
RUN chmod 755 /tmp/cleanup.sh
RUN cd /tmp && ./cleanup.sh data.csv add-header

# Add and run cleanup.py
ADD scripts/cleanup.py /tmp/cleanup.py
RUN cd /tmp && mv clean.csv clean.csv.bak && python3 cleanup.py clean.csv.bak clean.csv

# Switch back to solr user
USER solr

# Create the "scpa-scores" core
RUN /opt/solr/bin/solr start && \
    /opt/solr/bin/solr create_core -c scpa-scores && \
    /opt/solr/bin/solr stop
# Replace the schema file
COPY conf /apps/solr/data/scpa-scores/conf/

# Load the data to scpa-scores core
RUN /opt/solr/bin/solr start && sleep 3 && \
    curl 'http://localhost:8983/solr/scpa-scores/update?commit=true' -H 'Content-Type: text/xml' --data-binary '<delete><query>*:*</query></delete>' && \
    curl -v "http://localhost:8983/solr/scpa-scores/update/csv?update.chain=script&commit=true&f.instrumentation.split=true&f.instrumentation.separator=,&f.special.split=true&f.special.separator=|" \
    --data-binary @/tmp/clean.csv -H 'Content-type:text/csv; charset=utf-8' && \
    /opt/solr/bin/solr stop
    
FROM solr:8.1.1-slim

ENV SOLR_HOME=/apps/solr/data

USER root
RUN mkdir -p /apps/solr/

USER solr
COPY --from=builder /apps/solr/ /apps/solr/
