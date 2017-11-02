# CS3219-A5

To start it up, you can install all the dependencies manually, or simply install Docker and run:
`docker-compose up`

This will automatically start Python Flask, MongoDB and populate the DB, all inside a lightweight VM. Access the site at:
`http://localhost:5000/`

(if you make any changes to the Dockerfiles, you can update with: `docker-compose down && docker-compose up --build`)
