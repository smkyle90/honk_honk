CONTAINER_NAME=imgs

xhost +local:

docker run -it --rm --network host --privileged \
  -v $(pwd):/${CONTAINER_NAME}:rw \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --name=${CONTAINER_NAME} \
  ${CONTAINER_NAME}:cpu \
  python3 writer.py

xhost -local: