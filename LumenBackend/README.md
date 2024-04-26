# LumenBackend

Backend server, serving a prediction model for the lumen competition

## How to run?

After you've cloned the repository you need to do the following:

- First step is to download docker, for windows the easiest way is to download the docker desktop app from [here](https://www.docker.com/products/docker-desktop/) . **Note** : For you to be able to run the app using the approach described bellow, it is necessary for docker to be already running.
- Navigate to the root of the cloned project and type: `docker compose up --build` , this will build the docker image and install all of the app requirements. **You do this only the first time when running the app** . With this you have successfully started our backend server
- Every other time, running the app is done by typing `docker compose up`

## How to test?

Sending requests to our backend server can be done through a api managment tool.

- There are many options and extensions for this, but the most popular one is postman. Postman can be downloaded from [here](https://www.postman.com/downloads/)
- After downloading postman you would just create a new request with some url. For example in our app to get the prediction you would send a POST request to `http://127.0.0.1:5000/predict/`
  - When recieving a request our server expects some data as well. We can do this by adding a body to our request in postman. The body should be in raw format and you can select json as text formatter. For example the body for our predict endpoint should look something like this:
    ```json
    {
      "start_date": "20.1.2009",
      "end_date": "25.1.2009"
    }
    ```
