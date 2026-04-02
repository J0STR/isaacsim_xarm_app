import socket
import cv2
import numpy as np

def main():
    # Start Socket
    UDP_IP = "127.0.0.1"
    UDP_PORT = 12345    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    # Increase the OS receive buffer size
    # Default is often too small (64KB), which causes dropped frames.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 2) # 2MB buffer

    print(f"Receiver started on {UDP_IP}:{UDP_PORT}. Press 'q' in any window to quit.")

    cam_names = {
        0: "Top View Cam",
        1: "Right Wrist Cam",
        2: "Left Wrist Cam"
    }

    try:
        while True:
            data, addr = sock.recvfrom(65535)
            
            if not data:
                continue

            # Extract Camera ID and Image Data
            cam_id = data[0]         # First byte is the ID
            jpeg_data = data[1:]     # Rest is the JPEG encoded image

            # Decode JPEG to OpenCV image
            nparr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # Show in corresponding window
                window_name = cam_names.get(cam_id, f"Unknown Camera {cam_id}")
                cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nShutting down receiver...")
    finally:
        sock.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()