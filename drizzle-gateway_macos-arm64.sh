# pull latest version
docker pull ghcr.io/drizzle-team/gateway:latest

# persistent volume is required for configuration file
docker volume create drizzle-gateway

# start the studio
docker run -d \
  --name drizzle-gate \
  --restart always \
  -p 4983:4983 \
  -e PORT=4983 \ # Set the port for Drizzle Gateway (optional)
  -e STORE_PATH=./app \ # Set your store path (optional)
  -e MASTERPASS=your_master_password \ # Set your master pass (optional)
  -v drizzle-gateway:/app \
  ghcr.io/drizzle-team/gateway:latest

# Once Drizzle Gateway is running, you can access it via the web interface at http://localhost:4983
