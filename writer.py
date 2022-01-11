from imgs import Imager, Pubber
import time

if __name__ == '__main__':
	addr = "*"
	port = "5556"

	pubber = Pubber(addr, port)
	img = Imager()

	while True:
		img.read()
		img_json = img.as_json()
		pubber.pub(img_json)
		time.sleep(1)
