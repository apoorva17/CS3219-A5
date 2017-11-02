FROM mongo:3

ADD ./data.json /config/data.json
WORKDIR /config
CMD mongoimport --host mongodb --db cir --collection papers --type json --file ./data.json
