import queue
import cv2

def udp_sender_worker(image_queue: queue.Queue, udp_socket, dest_addr):
    """ Background thread to compress and send images """
    while True:
        try:
            # Wait for an image from the main loop
            frames = image_queue.get(block=True)
            if frames is None: 
                break # Exit signal
            
            # Process all 3 cameras
            for i, data in enumerate(frames):
                if data is not None and i<=2:
                    # RGB Data
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
                    _, encoded_img = cv2.imencode('.jpg', data, encode_param)

                    # BGR Data
                    # bgr_data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
                    # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
                    # _, encoded_img = cv2.imencode('.jpg', bgr_data, encode_param)
                    
                    # Send with a small header so the receiver knows which cam it is
                    # Header: 1 byte for cam ID
                    header = bytes([i]) 
                    udp_socket.sendto(header + encoded_img.tobytes(), dest_addr)
                else:
                    joint_header = bytes([3])
                    udp_socket.sendto(joint_header + data.tobytes(), dest_addr)
            
            image_queue.task_done()
        except Exception as e:
            print(f"Worker Error: {e}")