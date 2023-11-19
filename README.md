# BD_Project_Distributed_Load_Testing

## Set up dev env

### Note in the compose file that we are not running it in the debug mode. Results may be different in that case.

You can now specify the number of driver nodes you want using the command

`docker-compose up -d --scale driver_node <number_of_driver_nodes>`

For 8 driver nodes http://localhost:5000/ must appear like this

![Screenshot (20)](https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/d61caa56-8a7d-4326-b20e-6e944feacc98)

All logs could be inspected using Docker Desktop or running `docker logs <container_id>`

Shut down all containers using 

`docker-compose down`

## Trouble Shooting docs

The most common error faced was NoBrokersAvailableError()

Fix it by bring all containers down and then up again using the commands above

or adjust time.sleep() in app.py of all 3 folders to make sure kafka has enough time to be set up completely

or make sure bootstrap_servers argument matches with the name of the kafka container in your system which shouldnt be an issue if folder name is `bd_project_distributed_load_testing.`
