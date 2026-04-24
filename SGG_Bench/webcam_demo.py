import cv2
import numpy as np
import onnxruntime as ort
import argparse

from standalone_onnx_demo import SGG_ONNX_Standalone


class SGG_ONNX_Webcam(SGG_ONNX_Standalone):
    def __init__(self, onnx_path, provider="CUDAExecutionProvider", rel_conf=0.1, box_conf=0.5):
        super().__init__(onnx_path, provider, rel_conf, box_conf)

    def run(self):
        cap = cv2.VideoCapture(0)  # Open the default webcam

        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            # Process the frame with the ONNX model
            output = self.predict(frame, visualize=True)

            # Display the output (for demonstration purposes)
            cv2.imshow('SGG ONNX Webcam Demo', output[3])

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # get the onnx path from command line arguments
    parser = argparse.ArgumentParser(description="Run SGG ONNX model on webcam feed.")
    parser.add_argument('--onnx_path', type=str, required=True, help='Path to the ONNX model file.')
    parser.add_argument('--rel_conf', type=float, default=0.1, help='Relation confidence threshold.')
    parser.add_argument('--box_conf', type=float, default=0.5, help='Box confidence threshold.')
    parser.add_argument('--provider', type=str, default='CUDAExecutionProvider',
                        choices=['CUDAExecutionProvider', 'TensorrtExecutionProvider', 'CPUExecutionProvider'],
                        help='ONNX Runtime execution provider')

    args = parser.parse_args()

    demo = SGG_ONNX_Webcam(args.onnx_path, provider=args.provider,
                           rel_conf=args.rel_conf, box_conf=args.box_conf)
    demo.run()