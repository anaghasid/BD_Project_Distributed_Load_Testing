# BD_Project_Distributed_Load_Testing

## Set up dev env

For the first time create the images and then run the containers using the command

`docker-compose up -d --build`

From the second time onwards since images are built run 

`docker-compose up -d`

#### NOTE - if you run it with --build flag images will be created again causing memory wastage.

All logs could be inspected using Docker Desktop or running `docker-compose logs <container_id>`

#### If all 6/6 containers are running then http://localhost:5000 will display something similar to the image attached below, where each node has registered to kafka using its ip_address and container_id

#### There is a good chance you will not get this result because we currently run flask in debug mode(best for development) which means the changes you make in the any file will be reflected in the containers while they are running. That's why when you visit localhost:5000 it causes rerender of the orchestrator but not the other nodes , so the consumer keeps listening for registration information and doesnt send data to localhost.

#### Remove the --debug flag while running flask in the docker-compose file and you will surely get the result below.

![Screenshot (18)](https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/d42101f2-7a5f-43d4-988c-a5690b89dce1)

Shut down all containers using 

`docker-compose down`

## Trouble Shooting docs

The most common error faced was NoBrokersAvailableError()

Fix it by bring all containers down and then up again using the commands above

or adjust time.sleep() in app.py of all 3 folders to make sure kafka has enough time to be set up completely

or make sure bootstrap_servers argument matches with the name of the kafka container in your system which shouldnt be an issue if folder name is `bd_project_distributed_load_testing.`
