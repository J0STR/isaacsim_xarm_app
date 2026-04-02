import socket
import cv2
import numpy as np
import struct
import queue

import socket
import cv2
import numpy as np
import struct

def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return data

def tcp_sender_worker(image_queue: queue.Queue, port: int, action_queue: queue.Queue,):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    print(f"TCP Server ready. Waiting for receiver on port {port}...")

    while True:
        try:
            client_conn, addr = server_socket.accept()
            print(f"Receiver connected: {addr}")
            
            while True:
                # This blocks until the main loop calls image_queue.put()
                data_list = image_queue.get()
                
                if data_list is None: # Shutdown signal
                    client_conn.close()
                    return

                # Unpack the data
                top_view, wrist_r, wrist_l, joints = data_list
                
                # Convert & Compress
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
                _, img0 = cv2.imencode('.jpg', top_view, encode_param)
                _, img1 = cv2.imencode('.jpg', wrist_r, encode_param)
                _, img2 = cv2.imencode('.jpg', wrist_l, encode_param)
                
                joint_bytes = joints.astype(np.float32).tobytes()
                img0_bytes = img0.tobytes()
                img1_bytes = img1.tobytes()
                img2_bytes = img2.tobytes()

                # Build the Header (4 unsigned ints = 16 bytes)
                # Format: JointLen, Img0Len, Img1Len, Img2Len
                header = struct.pack('IIII', len(joint_bytes), len(img0_bytes), len(img1_bytes), len(img2_bytes))
                
                # Send as one continuous block
                client_conn.sendall(header + joint_bytes + img0_bytes + img1_bytes + img2_bytes)

                size_header = recv_all(client_conn, 4)
                if size_header:
                    action_len = struct.unpack('I', size_header)[0]
                    action_raw = recv_all(client_conn, action_len)
                    if action_raw:
                        # Convert to (15, 16) array
                        action_chunk = np.frombuffer(action_raw, dtype=np.float32).reshape(15, 16)
                        action_queue.put(action_chunk)
                
        except (ConnectionResetError, BrokenPipeError):
            print("Receiver disconnected. Waiting for new connection...")
        except Exception as e:
            print(f"TCP Worker Error: {e}")