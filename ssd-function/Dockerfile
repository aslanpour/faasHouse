FROM --platform=${TARGETPLATFORM:-linux/arm64} openfaas/of-watchdog:0.7.7 as watchdog
#To build GPU enabled image, use dustynv/jetson-inference:r32.7.1 base image instead of python:3.7-slim-buster and uncomment lines titled "[GPU]".
#To build non-GPU enabled image, use python:3.7-slim-buster base image instead of dustynv/jetson-inference:r32.7.1 and comment  lines titled "[GPU]".
#Ro build for amd64, replace amd64 with amr64 in two places for base images.

#Image tag is assocciated to the Jetson Nano L4T version, obtain yours by cat /etc/nv_tegra_release and get relevant image from https://github.com/dusty-nv/jetson-inference/blob/master/docs/aux-docker.md#running-the-docker-container
# FROM --platform=${TARGETPLATFORM:-linux/arm64} dustynv/jetson-inference:r32.7.1
#[CPU/TPU]
FROM --platform=${TARGETPLATFORM:-linux/arm64} python:3.7-slim-buster

#Command to use this Docker image
#docker build --build-arg CACHEBUST=$(date +%s) --tag localhost:6000/image_name:image_tag .
#--build-arg CACHEBUST=$(date +%s) sets a new value for ARG CACHEBUST in the Dockerfile so after this line everything will be loaded again per build to avoid caching.
#To use TPU or GPU, container user must have root privileged or use "--user root" flag
#To use GPU, enable nvidia runtime on host level or container level by passing "--runtime nvidia" flag
#To use TPU, pass "--privileged" flag to the container (and for first use of TPU on a node, use "-v /dev/bus/usb:/dev/bus/usb"). Verify by docker inspect --format='{{.HostConfig.Privileged}}' [container_id]
#docker run -d -t -p 5000:5000 --privileged --user root -v /dev/bus/usb:/dev/bus/usb --name tpu <docker_image_name>
#docker exec -i -t gpu bash
#docker logs gpu

#In kubernetes, equivalent of --root is "runAsUser: 0" under securityContext.
#In kuberneets equivalent of --privileged is privilged: true under securityContext.
#Inkubernetes equivalent of -v /dev/bus/usb:/dev/bus/usb is to dfine volumes.

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

# RUN apk --no-cache add openssl-dev ${ADDITIONAL_PACKAGE}
# RUN apt install -y openssl-dev ${ADDITIONAL_PACKAGE}
RUN apt-get install openssl ${ADDITIONAL_PACKAGE}

# Uncomment if you want to use native modules
#RUN apt-get -qy update && apt-get -qy install gcc make

# Add non root user
# RUN addgroup -S app && adduser app -S -G app
RUN addgroup --system app && adduser app --system --ingroup app
RUN chown app /home/app

USER app
ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY index.py           .
#flask and waitress
COPY requirements.txt   .


#Installations

USER root
RUN apt-get -qy update
#Installs flask and waitress
RUN python3 -m pip install -r requirements.txt

#mostly for CPU/TPU, but also GPU -- 
RUN apt-get install -y git curl wget nano gnupg2 ca-certificates unzip tar usbutils udev
#Note: usbutils is for lsusb command that gets USB info, but this does not show Product info like Google Inc. in the container that is the name of Google TPU Coral, although it does in the host, so udevadm is installed by udev package to update usb info which is a known issue in some cases: Ref: https://www.suse.com/support/kb/doc/?id=000017623)
RUN udevadm trigger --subsystem-match=usb

#[TPU/CPU] Install TPU runtime
#Add the repository
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get -qy update

#install standard TPU (or with maximum frequency 'libedgetpu1-max')
#[TPU/CPU]
RUN apt-get install -y libedgetpu1-std

#Install python modules (names is only for GPU image)
RUN python3 -m pip install --upgrade pip && python3 -m pip install numpy Pillow argparse requests configparser names
RUN python3 -m pip install 'protobuf>=3.18.0,<4'

#Note:Tensorflow lite examples require protobuf>=3.18.0,<4, but not sure if not practising that will cause an issue. Ref: #Ref: https://github.com/tensorflow/examples/blob/master/lite/examples/object_detection/raspberry_pi/requirements.txt
#[CPU/TPU] 
RUN apt-get install -y python3-pycoral
RUN python3 -m pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0
#Note1 for pycoral: Although Pycoral package is installed, it might not be recognized, so it is reinstalled by the above command (https://coral.ai/software/#pycoral-api) 
#according to the discussion in here: https://github.com/google-coral/pycoral/issues/24. If this also did not work, build the wheel, 
#example: https://blogs.sap.com/2020/02/11/containerizing-a-tensorflow-lite-edge-tpu-ml-application-with-hardware-access-on-raspbian/
#Note2: by installing pycoral package, tflite-runtime and setuptools are also installed.
#Note3: Tensorflow Lite examples require tflite-support==0.4.0 to be installed but their code also works with tflite-runtime. Ref: #Ref: https://github.com/tensorflow/examples/blob/master/lite/examples/object_detection/raspberry_pi/requirements.txt
#Note4: connect TPU to USB 3; otherwise,  inferencing times actually increase by a factor of ×2 if mounted to USB 2. Ref https://www.hackster.io/news/benchmarking-the-intel-neural-compute-stick-on-the-new-raspberry-pi-4-model-b-e419393f2f97
#Note5: Original USB cable of Coral TPU wont probably work on USB 2 and has limitations in speed (5Gbps); to use USB 3 or better speed, (at least mount TPU to USB 3) use 10Gbps cables. Ref:https://github.com/tensorflow/tensorflow/issues/32743 and https://www.hackster.io/news/benchmarking-the-intel-neural-compute-stick-on-the-new-raspberry-pi-4-model-b-e419393f2f97
#Note6: For bare metal use, if ValueError: Failed to load delegate from libedgetpu.so.1, reboot the host. Ref: https://github.com/tensorflow/tensorflow/issues/32743
#Note7: You may need to add your linux user to plugdev group. Ref: https://github.com/tensorflow/tensorflow/issues/32743. As follows: sudo usermod -aG plugdev [your username]

##expected installations: python3 -m pip list
#Installed versions
#numpy          1.21.6
#Pillow         9.2.0
#pip            22.2.1
#protobuf       4.21.4
#pycoral        2.0.0
#setuptools     57.5.0
#tflite-runtime 2.5.0.post1
#wheel          0.37.1


RUN chown -R app:app *

# Build the function directory and install any user-specified components
USER app

#Code for CPU/TPU based on EdjeElectronics
#(ref. used for this code) EdjeElectronics: https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md
#note that EdjeElectroincs instruction is for ARMv7 and exactly following that may face error on ARM64, so I follow my own instruction.
#Alternative ref1: Google https://coral.ai/docs/accelerator/get-started/#3-run-a-model-on-the-edge-tpu
#Alternative ref2: Tensorflow Lite official: https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi


#Download models

WORKDIR /home/app/
RUN mkdir networks
RUN mkdir networks/tensorflow
RUN mkdir networks/tensorflow-lite
RUN mkdir networks/tensorrt

#Tensorflow Lite models. ref: https://coral.ai/models/all/#detection
#Note: The python code (i.e., function) at the moment works only on model V1 and throws an error when using model V2 due to the difference in image preprocessing requirements.
#Model 1: SSD-MobileNet-V1-300-300-TF1-90obj.
WORKDIR /home/app/networks/tensorflow-lite/
RUN mkdir SSD-MobileNet-V1-300-300-TF1-90obj
WORKDIR /home/app/networks/tensorflow-lite/SSD-MobileNet-V1-300-300-TF1-90obj/
#CPU model
RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/ssd_mobilenet_v1_coco_quant_postprocess.tflite -O model.cpu.tflite
#TPU model
#[TPU]
RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite -O model.edgetpu.tflite
#Labels
RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/coco_labels.txt -O labelmap.txt

#spare model for CPU/TPU
#Model 2: SSD-MobileNet-V2-300-300-3-TF2-90obj. 
#WORKDIR /home/app/networks/tensorflow-lite/
#RUN mkdir SSD-MobileNet-V2-300-300-3-TF2-90obj
#WORKDIR /home/app/networks/tensorflow-lite/SSD-MobileNet-V2-300-300-3-TF2-90obj/
#CPU model
#RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/tf2_ssd_mobilenet_v2_coco17_ptq.tflite -O model.cpu.tflite
#TPU model
#RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/tf2_ssd_mobilenet_v2_coco17_ptq_edgetpu.tflite -O model.edgetpu.tflite
#Labels
#RUN wget --content-disposition https://raw.githubusercontent.com/google-coral/test_data/master/coco_labels.txt -O labelmap.txt


#TensorRT models. ref: #links in jetson-inference/tools/downlaod-models.sh or this link https://github.com/dusty-nv/jetson-inference/blob/master/tools/download-models.sh
#Since TensorRT (jetson-inference) only recognizes ./networks/SSD-Mobilenet-v1/.. for model file location, we need to put GPU model files under /home/app/function/networks dir. 
#But, since handler.py is called from index.py which is in /home/app/ dir, then tensorrt models must locate in /home/app/networks/ dir.
#If one needs a different location, you may edit jetson-inference and rebuild it as suggested here https://forums.developer.nvidia.com/t/how-to-load-models-from-a-custom-directory/223016

#[GPU]
# WORKDIR /home/app/networks/
#Model 1: SSD-Mobilenet-v1
#GPU model
#[GPU]
# RUN wget https://nvidia.box.com/shared/static/0pg3xi9opwio65df14rdgrtw40ivbk1o.gz -O SSD-Mobilenet-v1.tar.gz
#Note: in some cases, downloading from box.com is blocked. In that case, use the below mirror link
# RUN wget https://github.com/dusty-nv/jetson-inference/releases/download/model-mirror-190618/SSD-Mobilenet-v1.tar.gz -O SSD-Mobilenet-v1.tar.gz
# RUN tar -xvzf SSD-Mobilenet-v1.tar.gz
# RUN rm -rf SSD-Mobilenet-v1.tar.gz
#This results in a new directory as SSD-Mobilenet-v1 that contains ssd_mobilenet_v1_coco.uff and ssd_coco_labels.txt
#upon the first inference use, TensorRT creates an engine that optimizes the inferences. This may take a while for the first run. To avoid this delay, we copy here a prebuilt engine for this model.

#Copy the engine prebuilt model to avoid first run delay. If you have not the engine file, run test_gpu_detection.py on the host to create one.
#[GPU]
# COPY ./networks/SSD-Mobilenet-v1/ssd_mobilenet_v1_coco.uff.1.1.8201.GPU.FP16.engine ./SSD-Mobilenet-v1/

#spare model for GPU
#Model 2: SSD-Mobilenet-v2
#[GPU]
#WORKDIR /home/app/networks/
#GPU model
#[GPU]
#RUN wget https://nvidia.box.com/shared/static/jcdewxep8vamzm71zajcovza938lygre.gz -O SSD-Mobilenet-v2.tar.gz
#Note: in some cases, downloading from box.com is blocked. Replace the mirror link: https://github.com/dusty-nv/jetson-inference/releases/download/model-mirror-190618/SSD-Mobilenet-v2.tar.gz
#RUN tar -xvzf SSD-Mobilenet-v2.tar.gz
#RUN rm -rf SSD-Mobilenet-v2.tar.gz
#This results in a new directory as SSD-Mobilenet-v2 that contains ssd_mobilenet_v2_coco.uff and ssd_coco_labels.txt

#No prebuilt engine file I created for this now.

#More models for Tensorflow Lite: (the models may require images to undergo a particular preprocessing)
#Model of EdjeElectronics (CPU/TPU) work on the python code already. Ref: from git clone https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi.git
#Google Models Lite CPU&TPU  https://coral.ai/models/all/
#More models for Tensorflow:
#From NVIDIA https://github.com/dusty-nv/jetson-inference/#object-detection where a label and .uff file is downloaded and in first execution TensorRT will create a GPU.FP16.engine file for itself.
#More models for Tensorflow and Tensorflow Lite:
#From Tensorflow Hub https://tfhub.dev/tensorflow/collections/object_detection/1

#Download test images
RUN mkdir -p /home/app/images
WORKDIR /home/app/images
RUN wget --content-disposition https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/test_images/image1.jpg -O image1.jpg
RUN wget --content-disposition https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/test_images/image2.jpg -O image2.jpg

#Codes
WORKDIR /home/app/

######
# USER app
# ENV PATH=$PATH:/home/app/.local/bin

# WORKDIR /home/app/

# COPY index.py           .
# #flask and waitress
# COPY requirements.txt   .

# USER root
# RUN apt-get -qy update
# #Installs flask and waitress
# RUN python3 -m pip install -r requirements.txt

# USER app
#######


#function files
RUN mkdir -p /home/app/function
WORKDIR /home/app/function/
RUN touch __init__.py
COPY function/requirements.txt	.
#This requirements.txt is empty for now
RUN python3 -m pip install --user -r requirements.txt

#install function code
USER root

#This needs a different value each time you build the image so it wont cache the application files and copies updated ones.
ARG CACHEBUST=1 

#The 'function' directory containes a handler.py file for object detections and load_inference_model.py. It is based on EdjeElectronics example code and edited to not use opencv. For Tensorflow Lite, you may follow examples in the Google Coral website for simplicity: https://coral.ai/docs/accelerator/get-started/#3-run-a-model-on-the-edge-tpu
#More demos can be found in the followings: https://medium.com/@techmayank2000/object-detection-using-ssd-mobilenetv2-using-tensorflow-api-can-detect-any-single-class-from-31a31bbd0691 and https://levelup.gitconnected.com/custom-object-detection-using-tensorflow-part-1-from-scratch-41114cd2b403
#Other coppied files: test_gpu_detection.py, test_config.py, test_pioss.py
COPY function/   .
RUN chown -R app:app ../
RUN touch __init__.py

# ARG TEST_COMMAND=tox
# ARG TEST_ENABLED=false
# RUN if [ "$TEST_ENABLED" == "false" ]; then \
#     echo "skipping tests";\
#     else \
#     eval "$TEST_COMMAND"; \
#     fi

WORKDIR /home/app/

#Allow tpu delegate for the user or run container as root; otherwise, it receives this error ValueError: Failed to load delegate from libedgetpu.so.1.0. Ref: https://github.com/tensorflow/tensorflow/issues/32743#issuecomment-543806766
USER root
#RUN usermod -aG plugdev app

#[TPU]
#To use TPU delegate, add app to root group 
RUN usermod -G root app
#and grant it root privilege
RUN usermod -u 0 -g 0 -o app
USER app

#configure WSGI server and healthcheck

ENV fprocess="python index.py"

ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
#CMD ['/bin/bash']