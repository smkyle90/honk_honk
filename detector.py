from imgs import Detector 


if __name__ == '__main__':
    addr = "192.168.0.207"
    port = "5556"

    show_video = False
    save_img = ["car", "truck"]

    d = Detector(addr, port, save_img, show_video)
    d.spin()