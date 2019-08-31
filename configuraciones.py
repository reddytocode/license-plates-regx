from openalpr import Alpr
from pydarknet import Detector

country = "bo"
config = "/etc/openalpr/openalpr.conf"
runtime_data = "/usr/share/openalpr/runtime_data"

def alpr_conf():
    alpr = Alpr(country, config, runtime_data)
    alpr.set_top_n(7)
    alpr.set_default_region("base")
    alpr.set_detect_region(False)
    return alpr
    
def network_conf():

    net = Detector(bytes("data/vehicle-detector/yolo-voc.cfg", encoding="utf-8"),
                   bytes("data/vehicle-detector/yolo-voc.weights", encoding="utf-8"),
                   0,
                   bytes("data/vehicle-detector/voc.data", encoding="utf-8"))
    return net