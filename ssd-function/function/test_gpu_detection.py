#!/usr/bin/env python3
#locate this files and run python3 test_gpu_detection.py
#model_full_path='./networks/SSD-Mobilenet-v1/ssd_mobilenet_v1_coco.uff',
#labels_full_path='./networks/SSD-Mobilenet-v1/ssd_coco_labels.txt', 
#test_image_full_path='/home/ubuntu/object-detection/ssd-gpu/images/image1.jpg', 


#This will run and build the engine file for this model (in a few minutes) so this model can later on use GPU in an optimized manner through TensorRT. 
#The created engine file will be added to the networks/model_name/directory

#The tail of output of this program should look like 

#[TRT]    ------------------------------------------------
#[TRT]    Timing Report networks/SSD-Mobilenet-v1/ssd_mobilenet_v1_coco.uff
#[TRT]    ------------------------------------------------
#[TRT]    Pre-Process   CPU   0.08854ms  CUDA   1.16651ms
#[TRT]    Network       CPU  31.08692ms  CUDA  29.98870ms
#[TRT]    Post-Process  CPU   0.08552ms  CUDA   0.08490ms
#[TRT]    Visualize     CPU   0.16459ms  CUDA   5.26396ms
#[TRT]    Total         CPU  31.42557ms  CUDA  36.50406ms
#[TRT]    ------------------------------------------------
#
#[TRT]    note -- when processing a single image, run 'sudo jetson_clocks' before
#                to disable DVFS for more accurate profiling/timing measurements



# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils
import time

print('GPU object detection loaded.')

#Note that in fact only --network is recognized and this name must follow the build-in names in jetson-inferecne listed here https://github.com/dusty-nv/jetson-inference/blob/384ce60e6ab434bdff5f1973bf4395dcdc9f017d/c/detectNet.h#L64
#By setting the --network, jetson-inference, looks for a directuroy as ./networks/model_dir_name_/model_uff file and label file.
#Hence, model file must be in the current directory under networks with a subdirectory and file names defined in jetson-inference.
# If one need to change directories or file names, edit jetson-inference package and rebuild it like https://forums.developer.nvidia.com/t/how-to-load-models-from-a-custom-directory/223016

def initialize_gpu_model(model_name='ssd-mobilenet-v1',
                        model_full_path='./networks/SSD-Mobilenet-v1/ssd_mobilenet_v1_coco.uff',
                        labels_full_path='./networks/SSD-Mobilenet-v1/ssd_coco_labels.txt', 
                        test_image_full_path='/home/app/images/image1.jpg', 
                        inference_test_repeat=10,
                        threshold=0.5):

    print('Initialize GPU model started.')
    print('Requested setup:' + 
        '\nmodel_name= ' + model_name +
        '\nlabels_full_path= ' + labels_full_path +
        '\ntest_image_full_path= ' + test_image_full_path +
        '\ninference_test_repeat= ' + str(inference_test_repeat) +
        '\nthreshold= ' + str(threshold)) 

    start_main = time.time()

    #load model
    start = time.time()
    #net = jetson.inference.detectNet(model_name, threshold=0.5)
    net = jetson.inference.detectNet(argv=['--network=' + model_name], threshold=0.5)
    print('GPU Model ' + model_name + ' loaded in ' + str(time.time() - start) + ' sec')

    #read labels
    print('Load labels file')
    labels = []
    with open(labels_full_path) as file:
        for line in file:
            labels.append(line.rstrip("\n"))

    from PIL import Image
    #get test image
    print('Get test image')

    raw_image = Image.open(test_image_full_path)
    if hasattr(raw_image, 'filename'):
        print(raw_image.filename)
    name=raw_image.filename.split('/')[-1]
    print(name)
    raw_image.save(name)
    raw_image.close()
    #this can directly get fille full path to load an image without using Pillow if the image is stored on the host, and is not opened by Image.open.
    img_cuda = jetson.utils.loadImage(name)
    
    import os
    #os.remove(name)

    #run inference 10 times
    first_inference_response_time = 0
    avg_response_time = 0
    response_time = 0
    detected_objects = []
    for i in range(inference_test_repeat):
        start = time.time()
        #detection
        detections = net.Detect(img_cuda)
        response_time = time.time() - start
        
        if i == 0: 
            first_inference_response_time = response_time
        else: 
            avg_response_time += response_time

        print('Inference #' + str(i) + ' in ' + str(response_time) + ' sec')
        
        #get objects
        #detected_objects = []
        for detection in detections:
            #print(detection)
            label = labels[detection.ClassID]
            confidence = detection.Confidence
            #other obtained values by detection are Left, Top, Right, Bottom, Width, Height, Area and Center
            detected_objects.append({"object": label, "confidence": confidence})

        #print("detect............")
        for object in detected_objects:
            print(object)
            
    # print out performance info
    if inference_test_repeat > 1:
        avg_response_time = avg_response_time/(inference_test_repeat-1)
        print('avg resonse time (excluding first inference) = ' + str(avg_response_time))
    else:
        print('response time = ' + str(response_time))
    net.PrintProfilerTimes()

    elapsed_total = time.time() - start_main
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    output =  {"elapsed_total": elapsed_total, 
            "avg_response_time_excluding_the_first_inference": avg_response_time, 
            "first_inference_response_time": first_inference_response_time,
            "sum__different_detected_objects": detected_objects,
            "Note": "repeated detected_objects are ignored to report."}
    print(output)

    return(output)

initialize_gpu_model()