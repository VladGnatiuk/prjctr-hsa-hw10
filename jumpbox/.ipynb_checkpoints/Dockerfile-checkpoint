FROM python:3.11-slim

# Create a non-root user
ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

WORKDIR /app

COPY requirements.txt /tmp/
COPY requirements.dev.txt /tmp/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.dev.txt \
    && rm /tmp/requirements.txt \
    && rm /tmp/requirements.dev.txt

# Configure Jupyter for the non-root user
USER $USERNAME
RUN jupyter notebook --generate-config \
    && echo "c.NotebookApp.ip = '0.0.0.0'" >> /home/$USERNAME/.jupyter/jupyter_notebook_config.py \
    && echo "c.NotebookApp.open_browser = False" >> /home/$USERNAME/.jupyter/jupyter_notebook_config.py \
    && echo "c.NotebookApp.token = ''" >> /home/$USERNAME/.jupyter/jupyter_notebook_config.py

# Keep container alive
CMD ["sleep", "infinity"]