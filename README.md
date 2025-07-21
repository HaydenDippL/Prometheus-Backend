# Prometheus Backend

A simple dockerized python reverse proxy to interact with the Kalshi API

## Docker

Run the app
```
docker-compose up
```

Build and run the app
```
docker-compose up --build
```

## Local

### With Miniconda

Create environment from yml
```
conda env create -f environment.yml
```

Activate environment
```
conda activate prometheus
```

Deactivate environment
```
conda deactivate
```

---

Everytime you install a new package make sure to add it to the requirements.txt file

### With Python

Install requirements
```
pip install -r requirements.txt
```

Run app
```
python3 app.py
```

---

Everytime you install a new package make sure to add it to the requirements.txt file