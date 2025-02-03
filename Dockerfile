
 # get an image using the techstack of your app
 FROM python:3.8 

 #  create a working directory for the app
 WORKDIR /app

 # copy requirements.txt file to the /app directory
 COPY requirements.txt ./requirements.txt

 # run the app
 RUN pip install -r requirements.txt
 
 # Export the port your app is running on
 EXPOSE 8501

 # copy all to the app directory
 COPY . /app

 # get an entry point for the app OR CMD streamlit app.py
 ENTRYPOINT ["streamlit", "run"]
 CMD ["app.py"]

