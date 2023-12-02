# BD_Project_Distributed_Load_Testing

### The project specifications are listed listed in the Distributed_Load_Testing.pdf file.

### This project aims to conduct distributed load testing using Docker containers to simulate kafka, orchestrator , driver and target server nodes.

To start the distributed load testing run the command 

`docker-compose up -d --scale driver_node=<number_of_driver_nodes>`

***Note:*** The tests haven't been run with more than 8 driver nodes. ***Try at your own risk.***

After a successful startup, the driver nodes register and send heartbeats to the orchestrator node, as demonstrated in the video below for 8 driver nodes.

https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/2ab6972d-0f64-4484-82ec-7a12ff121d5f

### The definitions of tsunami and avalanche testing are listed in the Distributed_Load_Testing.pdf

### Tsunami Testing
Video demonstration of tsunami testing is attached below.

https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/319f2981-a11b-48a1-82fb-45e6de2e49e6

### Avalanche Testing
Video demonstration of avalanche testing is attached below.

https://github.com/anaghasid/BD_Project_Distributed_Load_Testing/assets/112763290/698e2bc0-89f2-42c4-806b-a364354463af

Shut down all containers using 

`docker-compose down`

## Trouble Shooting docs

All logs could be inspected using Docker Desktop or running `docker logs <container_id>`

The most common error faced was NoBrokersAvailableError()

Fix it by bring all containers down and then up again using the commands above

or adjust time.sleep() in app.py of all 3 folders to make sure kafka has enough time to be set up completely

or make sure bootstrap_servers argument matches with the name of the kafka container in your system which shouldnt be an issue if folder name is `bd_project_distributed_load_testing.`
