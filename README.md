# Project Deployment

Follow these steps to deploy the web server on your Raspberry Pi.

## 1. Clone the Repository

Clone the repository to your desired location using the following command:
```git clone https://github.com/nuttysunday/certitestor-deployment.git```

## 2. Install Docker

### For Raspberry Pi

1. Install Docker:
   ```
   curl -sSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   docker --version
   ```

2. Install Docker Compose:
   ```
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
   sudo chmod +x /usr/bin/docker-compose
   docker-compose --version
   ```

For other platforms, refer to the official Docker documentation: [Install Docker](https://www.docker.com/products/docker-desktop/).

## 3. Start the Containers

Open the terminal in the directory where the `docker-compose.yml` file is located and to run the containers in detached mode:
```
sudo docker-compose up -d
```

## 4. Access the Application on Raspberry Pi

Open your browser and navigate to:
[http://127.0.0.1:7784](http://127.0.0.1:7784)

## 5. Access the Website on the Network

To access the website from other devices on your network:

1. Open port 7784 on the host machine. On Raspberry Pi, this can be done using:
   ```
   sudo firewall-config
   ```
   For more details, refer to: [How to Open a Raspberry Pi Linux Port](https://raspberrypi.stackexchange.com/questions/69123/how-to-open-a-raspberry-pi-linux-port).

2. Ensure you are on the same network and your Raspberry Pi has a static IP address. 

3. Access the application using:
   ```http://<IP_ADDRESS>:7784```

Replace `<IP_ADDRESS>` with the static IP address of your Raspberry Pi.