CONTAINER_NAME=imgs


if [ ! -f yolov4.weights ]; then
    echo "Weights not found, downloading."
    wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights \
    -O yolov4.weights
fi



xhost +local:

docker run --gpus all -it --rm --network host --privileged \
  -v $(pwd):/${CONTAINER_NAME}:rw \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --name=${CONTAINER_NAME} \
  imgs:gpu \
  python3 detector.py

xhost -local: