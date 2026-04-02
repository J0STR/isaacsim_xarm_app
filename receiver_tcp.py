import socket
import cv2
import numpy as np
import struct
import time


def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return data


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 12345))
    print("Connected to Isaac Sim. Waiting for events...")

    data_names = {
        0: "top_down",
        1: "wrist_right",
        2: "wrist_left"
    }

    try:
        while True:
            # Read Header
            obs_dict = {}
            header_raw = recv_all(sock, 16)
            if header_raw is None: 
                break
            start = time.perf_counter()
            j_len, i0_len, i1_len, i2_len = struct.unpack('IIII', header_raw)
            
            # Read Payload based on header
            joint_data = recv_all(sock, j_len)
            img0_data = recv_all(sock, i0_len)
            img1_data = recv_all(sock, i1_len)
            img2_data = recv_all(sock, i2_len)

            if any(v is None for v in [joint_data, img0_data, img1_data, img2_data]):
                break
            
            # Receive
            joints = np.frombuffer(joint_data, dtype=np.float32)
            frame_top_view = cv2.imdecode(np.frombuffer(img0_data, np.uint8), cv2.IMREAD_COLOR)            
            frame_wrist_right = cv2.imdecode(np.frombuffer(img1_data, np.uint8), cv2.IMREAD_COLOR)            
            frame_wrist_left = cv2.imdecode(np.frombuffer(img2_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Make Dict
            joints_right = joints[:8]
            joints_left = joints[8:]            
            for i, angle in enumerate(joints_right):  # store angle,velocity and effort
                if i<7:
                    obs_dict[f"right_joint_{i+1}.pos"] = angle
                else:
                    obs_dict["right_gripper.pos"] = angle
            for i, angle in enumerate(joints_left):  # store angle,velocity and effort
                if i<7:
                    obs_dict[f"left_joint_{i+1}.pos"] = angle
                else:
                    obs_dict["left_gripper.pos"] = angle
            obs_dict[data_names[0]] = frame_top_view
            obs_dict[data_names[1]] = frame_wrist_right
            obs_dict[data_names[2]] = frame_wrist_left

            cv_converted_frame = cv2.cvtColor(obs_dict[data_names[0]], cv2.COLOR_RGB2BGR)            
            window_name = data_names.get(0, f"Unknown Camera {0}")
            cv2.imshow(window_name, cv_converted_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            end = time.perf_counter()

    except KeyboardInterrupt:
        sock.close()
    finally:
        sock.close()


if __name__ == "__main__":
    main()