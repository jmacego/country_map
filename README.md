# To run
```
docker-compose up
```

# To build requirements.txt
```
docker-compose down && docker-compose up -d
docker-compose exec app /bin/bash
pip-compile requirements.in
sudo chown jmac . -R
docker-compose build --no-cache
sudo chown -R 999:999 ./instance/postgres_data
sudo chmod -R 700 ./instance/postgres_data
```

# Flask Migration
```
docker-compose down && docker-compose up -d
docker-compose exec app /bin/bash
flask db init
flask db migrate -m "Add Retirement model"
flask db upgrade
```