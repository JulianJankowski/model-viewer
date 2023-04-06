# STL Model Viewer

This is a small web app to sort and view a large library of STLs without needing to download them from a NAS or similar device. This app is designed to be installed using Docker, mounting a folder in the static folder (e.g. /static/models/) to your existing root directory of your stls. Alternatively, you can just move your files into this folder directly, and run the we app itself. 

This app uses https://github.com/omrips/viewstl to view stls

## Setup
These instructions are for use of docker in a CLI environment
1. Ensure your have docker installed, and the docker daemon is running
2. While in the root directory, run `docker image build -t model-viewer .` to create your docker image
3. Run `docker run -d model-viewer <PARAMS>` to create your docker container. Note, in this command you specify the port you wish to run the web server on, as well as the directory of the stls you want to use.
4. Connect to 127.0.0.1:5000 to start using the app

If running directly from the CLI, you can also
1. Ensure you have python3 and flask installed
2. Move files into the /static/models/ folder
3. Use `flask run` to start the app

## Settings
The URL setting can be changed to specify the subfolder of the `static` folder from which the app starts to read the stl files.
