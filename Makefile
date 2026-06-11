.PHONY: run_mysql

run_mysql:
	docker run --name mysql_container \
		-e MYSQL_ROOT_PASSWORD=root \
		-e MYSQL_DATABASE=testdb \
		-p 3306:3306 \
		-d \
		mysql:latest

.PHONY: stop_mysql

stop_mysql:
	docker stop mysql_container
	docker rm mysql_container

mysql_cli:
	docker exec -it mysql_container mysql -u root -proot


install_reqs:
	pip install -r msg_service/requirements.txt
	pip install -r ws_service/requirements.txt
	pip install -r client_app/requirements.txt
	#pip install -r connect_service/requirements.txt



make run:
	docker compose down -v
	docker-compose up
