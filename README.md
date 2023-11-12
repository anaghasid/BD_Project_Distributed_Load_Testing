# BD_Project_Distributed_Load_Testing

## Set up dev env

pull if already cloned else clone

Create the image for driver node

`cd driver`

`docker build driver-node:1.0 .`

then for orchestrator node

`cd orchestrator`

`docker build orchestrator-node:1.0 .`

and finally the image for the target server

`cd orchestrator`

`docker build target-server:1.0 .`

### NOTE - First command might take some time, all others will be relatively faster because of caching.

Create the containers using 

`docker-compose up -d`

All logs could be inspected using Docker Desktop or running `docker-compose logs <container_id>`

#### If all 6/6 containers are running then http://localhost:5000 will display something similar to this where each node has registered to kafka using its ip_address and container_id

![Screenshot (18)](https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/d42101f2-7a5f-43d4-988c-a5690b89dce1)

Shut down all containers using 

`docker-compose down`

## Trouble Shooting docs

The most common error faced was NoBrokersAvailableError()

Fix it by bring all containers down and then up again using the commands above

or adjust time.sleep() in app.py of all 3 folders to make sure kafka has enough time to be set up completely

or make sure bootstrap_servers argument matches with the name of the kafka container in your system which shouldnt be an issue if folder name is `bd_project_distributed_load_testing.`



