import os
from imageai.Detection import ObjectDetection
from camera import Camera

cam = Camera().start()
execution_path = os.getcwd()

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(os.path.join(execution_path, "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()
detections = detector.detectObjectsFromImage(
	#input_image=os.path.join(execution_path, "image.jpg")
	input_image=cam.read()[1]
	, output_image_path=os.path.join(execution_path, "imagenew.jpg")
	#, extract_detected_objects=True
	, input_type="array"
	#, output_type="array"
)

for obj in detections:
	print(obj["name"], ": ", obj["percentage_probability"])

cam.stop()