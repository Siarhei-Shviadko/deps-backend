# deps-backend
________________________________________________________________________

Release startegy:
- Features brunch (and other) have options for manual deploy to DEV ENV.
- Merge to develop will start deploy to QA ENV
- Merge to master will start deploy to DEMO ENV
________________________________________________________________________

## Requirements

- docker >= 18.06.0
- docker-compose >= 1.23.0
- make >= 4.3

## Usage

Make sure that root deps is up and running

Do the following commands

```bash
# Setup environment variables for run
make install

# Fill required variables in .env file. 
# Actual information about variables could be found at KB onboarding page

# login to artifactory, use your EPAM credentials
make login

# update submodules
git submodule update --init --recursive

# run services
make run

# load migrations
make migrate

# load all fixtures
make load-fixtures

# run tests and linters
make ci
```

## Useful commands

In the root folder you can find `Makefile`, it contains shortcuts for useful commands, please read it and use for development.
`Makefile` adds one more layer of abstraction to simplify usage.

### Service status

To show service status you can run the following command

```bash
> docker-compose ps

         Name                       Command               State             Ports         
------------------------------------------------------------------------------------------
deps-backend_api_1        python -m deps_documents serve   Up         0.0.0.0:8001->8000/tcp
deps-backend_fixtures_1   /app/entrypoint.sh update      Exit 0                           
deps-backend_migrator_1   /app/entrypoint.sh update      Exit 0                         
deps-backend_solaris_1    python -m deps_documents lisen   Up  
```

### Build

To rebuild service run command

```bash
docker-compose build api
```

### Logs

To show service logs run the following command

```bash
docker-compose logs --tail=100 api
```

Service will write errors into this log

### Reload

To reload specific service if it's fail you can use

```bash
docker-compose restart api
```

### Tests and Linters

Before pushing code to remote, make sure you run `make ci` command run tests and code linters

### Fixtures

Note that if you want to load only specific fixtures, you can use the following command

```bash
docker-compose up -d fixture update --context="deps"
```

You can change context to load fixtures that you need
<span style="color:yellow">*</span> 
```python
["none", "user", "role"]

### Run locally using skaffold 
 Make sure that deps-infra (postgres, redis, rabbitmq is up) is up and running
 
# !Note make sure that context is rancher-desktop
```bash 
kubectl config current-context 
```

Do the following commands

```bash
make skaffold
```

## Enabling/Disabling vault usage
You can enable or disable vault secret usage without modifying kubernetes yaml files. By default vault usage is set to false inside value.yaml file but we override this value with VAULT_ENABLE_DEV, VAULT_ENABLE_QA, VAULT_ENABLE_INS, VAULT_ENABLE_DEMO, VAULT_ENABLE_DS variables from Settings >> CI/CD for each environment. If you change variable value from Settings >> CI/CD you need to manually start new pipline from CI/CD >> Pipelines.
