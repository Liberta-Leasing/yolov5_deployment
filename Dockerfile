FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y make curl wget sudo git gcc-c++ libgl1 libgl1-mesa-glx mesa-libGL ffmpeg libsm6 libxext6 poppler-utils

RUN yum install python3 python3-pip -y

ENV TZ=Europe/Paris

ARG DEBIAN_FRONTEND=noninteractive

RUN yum -y install git

WORKDIR "${LAMBDA_TASK_ROOT}"

COPY yolov5/requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY yolov5/hub.py ${LAMBDA_TASK_ROOT}/torch

COPY yolov5/app.py .

CMD ["app.lambda_handler"]
