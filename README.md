#### Meta Data Extraction App

+ Packages:
```bash
pip install
```
    - streamlit
    - streamlit.components.v1
    - numpy
    - pandas
    - pillow
    - exifread
    - seaborn
    - matplotlib
    - pyPDF2
    - mutagen
    - tinytag
    - docx2txt
    - python docx
    - PIL
    - PyPDF
    - doc2txt
    - os
    - uuid
    - eyed3
    - io


#### App Structure
+ Home
+ Image
+ Audio
+ PDF/Docx
+ About
  - Monitor
  - Stats of Uploads


#### Refactor & Tweaking:
radon : static code analysis
    - mi: maintainable
    - cc: cyclomatic complexity
    - hal

vulture: to check the packages imported but not used

l/isort: sorting import

black:format

### Deploying the App:
+ Streamlit Sharing
+ Heroku
+ Docker
+ GCP
+ AWS
+ HCP
+ Azure
+ Waypoint*
+ Alibaba
+ Etc

### Deploying with Docker:
+ Docker is an open platform for developing, shipping and running applications in a container. It enables us to separate applications from their infrastructure so we can deliver software quickly.

### Requirements:
+ Install Docker
+ Create a Docker file: contains instructions on how you want to build and ship the app, which will be in the format of layers. Then the docker diamond or docker engine reads the dockerfile and builds a docker image. The docker image can be thought of as mini os that can be used to build the containers and run your app.
     - Go to the app's working directory.
     - Get requirements using `pipreqs` in the command prompt, on the app's working directory.
     - Use `echo. > Dockerfile` in the command prompt to create a Dockerfile in the working directory.
     - Write instructions for the build in the Dockerfile. 
     - Then build with `docker build -t img/tagname`. On windows, use `docker build -t your_appname . -f your_docker_filename`
     - You can display the contents of the docker file using `type Dockerfile` in the command prompt.
     - Use `docker -run -p:internalPort:ExternalPort image_name:latest` to build a container

+ App + Requirement.txt

Dockerfile -> Layers -> Docker image -> Container


#### Deploying with streamlit share:
+ Create an account on streamlit and link your github account.
+ You can deploy your app by connecting your `app_file.py` to the streamlit page. 
      + Note:
          -  I had to create `__init__.py` file because I ran into some `ModuleNotFoundError` and I wanted streamlit to treat the modules as packages.
          - I adjusted the import path statements for the modules to correct the `ModuleNotFoundError`.
          - I uploaded my `_pycache_` folder where the `app_utils.cpython-38.pyc` and `db_fxns.cpython-38.pyc`.
          
