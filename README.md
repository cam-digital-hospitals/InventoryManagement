# Inventory Management Starter Solution

## Deployment

### Docker compose

```bash
# Start server
docker compose up -d --build
# Stop server
docker compose down
```

### Kubernetes

Building the docker image:
```bash
# Note: this image should be in a registry that is accesible to k8s cluster
docker build --tag ghcr.io/cam-digital-hospitals/inv-mgmt:latest .
# This pushes the image to the ghcr.io container registry
# Note: it is assumed that you have logged into the ghcr.io registry with:
# echo $PAT | docker login ghcr.io --username $GITHUB_USERNAME --password-stdin
docker push ghcr.io/cam-digital-hospitals/inv-mgmt:latest
```

Install & uninstall:
```bash
# Apply k8s/deployment.yaml, k8s/service.yaml, k8s/ingress.yaml
# in the 'default' namespace
kubectl -n default apply -f k8s
# Clean up
kubectl -n default delete -f k8s
```

Useful commands:

```bash
# Deployment: inv-mgmt (container#1: inv-mgmt:8000)
# Service: inv-mgmt-svc:80
# Ingress: inv-mgmt-ingress http://localhost

# Check logs
kubectl -n default logs svc/inv-mgmt-svc -f

# Access to the container shell
kubectl -n default exec -it svc/inv-mgmt-svc -- bash
```

## Usage

Navigate to `localhost:8000` in a web browser.  
New items can be set up in the `Stock Management` tab. 

If you need to use the django admin page - for example to edit the unit cost or supplier link of an existing item,   
It can be accessed at `localhost:8000/admin` or is linked from the `Stock Management` tab.  
Log in with:  
- username: `admin`
- password: `shoestring`  
