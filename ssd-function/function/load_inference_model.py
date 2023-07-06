import os
import numpy as np
import importlib.util
import time



def gpu_inference(interpreter_worker, labels, image_full_path, repeat):
    #for gpu_inference and load_gpu_model functions
    import jetson.inference
    import jetson.utils
    import time

    error_gpu_inference = ""

    start = time.time()

    try:
        #get image
        img_cuda = jetson.utils.loadImage(image_full_path)

        #run inference X times
        first_inference_response_time = 0
        avg_response_time = 0
        response_time = 0
        detected_objects = []
        for i in range(int(repeat)):
            start = time.time()
            #detection
            detections = interpreter_worker.Detect(img_cuda)
            response_time = time.time() - start
            
            if i == 0: 
                first_inference_response_time = response_time
            else: 
                avg_response_time += response_time

            #print('Inference #' + str(i) + ' in ' + str(response_time) + ' sec')
            
            #get objects
            for detection in detections:
                #print(detection)
                label = labels[detection.ClassID]
                confidence = detection.Confidence
                #other obtained values by detection are Left, Top, Right, Bottom, Width, Height, Area and Center
                detected_objects.append({"object": label, "confidence": confidence})

            for object in detected_objects:
                print(object, flush=True)
                
        
        interpreter_worker.PrintProfilerTimes()

        elapsed_total = time.time() - start
        print('gpu_inference() lasted for ' + str(elapsed_total), flush=True)
        #print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        #output =  {"elapsed_total": elapsed_total, 
        #        "avg_response_time_excluding_the_first_inference": avg_response_time, 
        #        "first_inference_response_time": first_inference_response_time,
        #        "sum__different_detected_objects": detected_objects,
        #        "Note": "repeated detected_objects are ignored to report."}
        #print(output)
    except Exception as e:
        error_gpu_inference += '\n' + str(e)

    return error_gpu_inference


def load_gpu_model(MODEL_RUN_ON, MODEL_DIR_GPU, MODEL_GPU_FILE, MODEL_LABEL_FILE_GPU, MODEL_GPU_BUILTIN_NETWORK, MODEL_MIN_CONFIDENCE_THRESHOLD):
    interpreter_get, labels = None, None
    error_load_gpu = ""
    try:
        import jetson.inference
        import jetson.utils
    except Exception as e:
        error_load_gpu += 'Loading GPU model failed. \nMake sure you are using dustynv/jetson-inference:tag as the base container image.\nMake sure jetson-inference is part of the container image.\n' + str(e)
    import time
    
    

    print('Loading inference model:  \nMODEL_RUN_ON=' + MODEL_RUN_ON + '  \nMODEL_DIR_GPU=' + MODEL_DIR_GPU + ' \nMODEL_GPU_FILE=' + MODEL_GPU_FILE +  ' \nMODEL_LABEL_FILE_GPU=' + MODEL_LABEL_FILE_GPU, flush=True)

    #model builtin name defined by jetson-inference
    #Note that in fact only model_name is recognized and this name must follow the build-in names in jetson-inferecne listed here https://github.com/dusty-nv/jetson-inference/blob/384ce60e6ab434bdff5f1973bf4395dcdc9f017d/c/detectNet.h#L64
    #By setting the model_name, jetson-inference, looks for a directuroy as ./networks/model_dir_name_/model_uff file and label file.
    #Hence, model file smust be in the current directory under networks.
    # If one need to change this, edit jetson-inference package and rebuild it like https://forums.developer.nvidia.com/t/how-to-load-models-from-a-custom-directory/223016
    #Here builtin model named 'ssd-mobilenet-v1' is used.
    model_name = 'ssd-mobilenet-v1'
    model_full_path = MODEL_DIR_GPU + MODEL_GPU_FILE
    labels_full_path = MODEL_DIR_GPU + MODEL_LABEL_FILE_GPU

    #load model
    start = time.time()
    if len(error_load_gpu)==0:
        try:
            interpreter_get = jetson.inference.detectNet(argv=['--network=' + MODEL_GPU_BUILTIN_NETWORK], threshold=float(MODEL_MIN_CONFIDENCE_THRESHOLD))
            #if multiple args are needed, seperate them by comma inside this bracket.
            #Another way of defining a detectNet --> interpreter_get = jetson.inference.detectNet(MODEL_GPU_BUILTIN_NETWORK, threshold=MODEL_MIN_CONFIDENCE_THRESHOLD)

            print('GPU Model ' + model_name + ' loaded in ' + str(time.time() - start) + ' sec', flush=True)
        except Exception as e:
            print(e, flush=True)
            error_load_gpu = ('\nLoading GPU model failed.' +
            'Is the container ran as root (--user root)?' +
            '\nMODEL_GPU_BUILTIN_NETWORK=' + MODEL_GPU_BUILTIN_NETWORK + ' or MODEL_MIN_CONFIDENCE_THRESHOLD=' + str(MODEL_MIN_CONFIDENCE_THRESHOLD) + ' may be incorrect.\n' + str(e))
        


    #read labels
    if len(error_load_gpu)==0:
        print('Load labels file', flush=True)
        labels = []
        try:
            with open(labels_full_path) as file:
                for line in file:
                    labels.append(line.rstrip("\n"))
        except Exception as e:
            print(e, flush=True)
            error_load_gpu += '\nLoading labels file failed.\nlabels_full_path=' + labels_full_path + ' may be incorrect\n' + str(e)
        

    return interpreter_get, labels, error_load_gpu



#laod a model 
def load(MODEL_RUN_ON, MODEL_DIR, MODEL_DIR_GPU, MODEL_CPU_FILE, MODEL_TPU_FILE, MODEL_GPU_FILE, MODEL_LABEL_FILE, MODEL_LABEL_FILE_GPU, MODEL_GPU_BUILTIN_NETWORK, MODEL_MIN_CONFIDENCE_THRESHOLD, MODEL_IMAGE_SAMPLE1, MODEL_INFERENCE_REPEAT, MODEL_CPU_TPU_INTERPRETER_THREADS):
    start = time.perf_counter()
    
    error_load = ""

    interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels = None,None,None,None,None,None,None,None,None,None

    #If GPU, go its own procedure and finish.
    if MODEL_RUN_ON == 'gpu':
        interpreter_get, labels, error_load = load_gpu_model(MODEL_RUN_ON, MODEL_DIR_GPU, MODEL_GPU_FILE, MODEL_LABEL_FILE_GPU, MODEL_GPU_BUILTIN_NETWORK, MODEL_MIN_CONFIDENCE_THRESHOLD)
        
        if len(error_load) == 0:
            #test model and create the engine file if not exists. Note that TensorRT creates an engine file for the model upon the first inference for optimizations. This takes a few seconds/minutes, but is only done once.
            error_load += gpu_inference(interpreter_get, labels, MODEL_IMAGE_SAMPLE1, MODEL_INFERENCE_REPEAT)

        elapsed = time.perf_counter() - start
        print('Loading and testing model finished in ' + '%.1fms' % (elapsed * 1000), flush=True)

        return interpreter_get, labels, error_load


    #else CPU or TPU
    print('Loading inference model...  \nMODEL_RUN_ON=' + MODEL_RUN_ON + ' \nMODEL_DIR=' + MODEL_DIR + ' \nMODEL_CPU_FILE=' + MODEL_CPU_FILE + ' \nMODEL_TPU_FILE=' + MODEL_TPU_FILE + ' \nMODEL_LABEL_FILE=' + MODEL_LABEL_FILE, flush=True)
    
    

    

    # Import TensorFlow libraries
    
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        if MODEL_RUN_ON == 'tpu':
            from tflite_runtime.interpreter import load_delegate
    else:
        print('Tensorflow Lite is not installed, so lets use full Tensorflow')
        from tensorflow.lite.python.interpreter import Interpreter
        if MODEL_RUN_ON == 'tpu':
            from tensorflow.lite.python.interpreter import load_delegate


    # Get path to current working directory
    #CWD_PATH = os.getcwd()

    # Path to .tflite file, which contains the model that is used for object detection
    if MODEL_RUN_ON == 'cpu':
        PATH_TO_CKPT = os.path.join(MODEL_DIR , MODEL_CPU_FILE)
    elif MODEL_RUN_ON == 'tpu':
        PATH_TO_CKPT = os.path.join(MODEL_DIR , MODEL_TPU_FILE)
    else:
        print('ERROR: MODEL_RUN_ON must be either cpu or tpu, but ' + MODEL_RUN_ON + ' is detected.', flush=True)
        error_load +=  '\nERROR: MODEL_RUN_ON must be either cpu or tpu, but ' + MODEL_RUN_ON + ' is detected.' 
        return interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels, error_load

    # Path to label map file
    PATH_TO_LABELS = os.path.join(MODEL_DIR , MODEL_LABEL_FILE)

    start_label = time.perf_counter()
    # Load the label map
    try:
        with open(PATH_TO_LABELS, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        elapsed = time.perf_counter() - start_label
        print('labels loaded in ' + '%.1fms' % (elapsed * 1000) + ' from ' + PATH_TO_LABELS,  flush=True)
        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == '???':
            del(labels[0])
    except Exception as e:
        print('ERROR: labels file is not loaded where PATH_TO_LABELS=' + PATH_TO_LABELS + '\n' + str(e), flush=True)
        error_load +=  '\nERROR: labels file is not loaded where PATH_TO_LABELS=' + PATH_TO_LABELS + '\n' + str(e)
        return interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels, error_load


    # Load the Tensorflow Lite model.
    start_tf = time.perf_counter()
    # If using Edge TPU, use special load_delegate argument
    interpreter_get = None
    if MODEL_RUN_ON == 'tpu':
        try:
            # The value for load_delegate is different on MacOS and Windows
            interpreter_get = Interpreter(model_path=PATH_TO_CKPT,
                                experimental_delegates=[load_delegate('libedgetpu.so.1.0')], num_threads=int(MODEL_CPU_TPU_INTERPRETER_THREADS))
            #print(PATH_TO_CKPT)
        except Exception as e:
            print('Make sure --privileged --user root -v /dev/bus/usb:/dev/bus/usb is given to the container', flush=True)
            error_load += '\n Loading TPU model failed, where PATH_TO_CKPT=' + PATH_TO_CKPT
            error_load += '\nIn Docker, make sure user has root access (--user root), privileged (--privileged) and USB access (-v /dev/bus/usb:/dev/bus/usb).\nIn Kubernetes, include securityContext: privileged=true, runAsUser: 0 and give USB access\n' + str(e)
            return interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels, error_load
    else:
        #cpu
        try:
            interpreter_get = Interpreter(model_path=PATH_TO_CKPT, num_threads=int(MODEL_CPU_TPU_INTERPRETER_THREADS))
        except Exception as e:
            error_load += '\nLoading CPU model failed where PATH_TO_CKPT=' + PATH_TO_CKPT + '\n' + str(e)
            return interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels, error_load

    elapsed = time.perf_counter() - start_tf
    print('model loaded to tensorflow in ' + '%.1fms' % (elapsed * 1000) + ' from ' + PATH_TO_CKPT, flush=True)
    interpreter_get.allocate_tensors()

    # Get model details
    input_details = interpreter_get.get_input_details()
    output_details = interpreter_get.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    # Check output layer name to determine if this model was created with TF2 or TF1,
    # because outputs are ordered differently for TF2 and TF1 models
    outname = output_details[0]['name']

    if ('StatefulPartitionedCall' in outname): # This is a TF2 model
        boxes_idx, classes_idx, scores_idx = 1, 3, 0
    else: # This is a TF1 model
        boxes_idx, classes_idx, scores_idx = 0, 1, 2

    elapsed = time.perf_counter() - start
    print('Loading model finished in ' + '%.1fms' % (elapsed * 1000), flush=True)
    return interpreter_get, floating_model, input_mean, input_std, input_details, output_details, boxes_idx, classes_idx,scores_idx, labels, error_load
    