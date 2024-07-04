# Project Deployment

Follow these steps to deploy the web server on your Raspberry Pi.


<details>
<summary style="font-size: 22px;">Important instructions</summary>

1. Enter all the commands in the terminal.

2. Sometimes you may need to use sudo for running some commands.

3. Make sure 7784 port is free and no other container or service is running on it

4. Have docker installed on your machine.

   <details>
   <summary>Docker Installation for Raspberry Pi</summary>

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

   </details>
</details>



<details>
<summary style="font-size: 22px;">Easy installation (automatically)</summary>&nbsp;

   Description:- In this method, no code is required on the server, it downloads the pre built image from Dockerhub. We just just download the docker-compose file which fetches the certi tester software images from Dockerhub and then we spin up the container.

   ```
   mkdir certi_tester
   cd certi_tester
   ```

   ```
   curl -O https://raw.githubusercontent.com/nuttysunday/certi-tester-deployment/main/easy-installation/docker-compose.yml
   ```

   ```
   docker-compose up
   ```

   Enter this into browser:-
   ```
   http://127.0.0.1:7784/
   ```

   To update the image from Docker Hub and restart the container:
   ```
   docker-compose pull
   ```

   Recreate the containers with the latest images
   ```
   docker-compose up -d --force-recreate
   ```

</details>


<details>
<summary style="font-size: 22px;">Manual installation</summary>&nbsp;

Description:- In this method, we download the code from github, and the build our images locally.

#### 1. Clone the Repository

Clone the repository to your desired location using the following command:

```
git clone https://github.com/nuttysunday/certitestor-deployment.git
```

```
cd certitestor-deployment
```

#### 2. Start the Containers

Builds the image from scratch and runs the container in detached mode:
```
sudo docker-compose up --build -d
```

#### 3. Access the Application on Raspberry Pi

Open your browser and navigate to:
[http://127.0.0.1:7784](http://127.0.0.1:7784)


#### 4. Updating the local images.

Take the container down and build it again
```
sudo docker-compose down
```

```
sudo docker-compose up --build -d
```
</details>

<details>
<summary style="font-size: 22px;">Accessing the Website on the Network</summary>
&nbsp;

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
</details>