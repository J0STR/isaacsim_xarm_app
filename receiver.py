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

    data_names = {
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
            data_id = data[0]         # First byte is the ID
            payload = data[1:]
            if data_id <= 2:
                # Decode JPEG to OpenCV image
                nparr = np.frombuffer(payload, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Show in corresponding window
                    window_name = data_names.get(data_id, f"Unknown Camera {data_id}")
                    cv2.imshow(window_name, frame)
            else:
                joints = np.frombuffer(payload, dtype=np.float32)
        
                # Split them back up (8 joints each)
                joints_right = joints[:8]
                joints_left = joints[8:]
                
                # Clear line and print (so it doesn't spam your terminal)
                print(f"Right Joints: {joints_right[7]:.4f}")
                print(f"Left Joints: {joints_left[7]:.4f}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nShutting down receiver...")
    finally:
        sock.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()