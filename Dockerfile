FROM test-base:latest

MAINTAINER Yi Shan(Yi.Shan@microsoft.com)

# Add source files and scripts
RUN mkdir /opt/jupyter
WORKDIR /opt/jupyter
COPY ./src /opt/jupyter
COPY ./DB_Perf_Kit.ipynb /opt/jupyter

# Install Jupyter Server
RUN python3 -m pip install jupyter

# Install python libs
RUN python3 -mpip install matplotlib
RUN pip install pandas==0.22.0
RUN pip install numpy
RUN pip install statsmodels==0.9.0
RUN pip install scipy==1.1.0
RUN pip install boto3==1.0.0

COPY ./db_supervisord.conf /etc/supervisor/conf.d/
COPY ./startup.sh /opt/jupyter
CMD ["/opt/jupyter/startup.sh"]