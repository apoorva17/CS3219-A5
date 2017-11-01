FROM mongo:3

ADD ./data.json /config/data.json
WORKDIR /config
RUN mkdir -p /data/db && mongod --fork --logpath=/tmp/mongodb.log && sleep 20 && \
mongoimport --db cir --collection papers --type json --file ./data.json && mongod --shutdown
