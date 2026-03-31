# Check out the standalone examples for more details on different implementations
# - Linux: ~/.local/share/ov/pkg/isaac_sim-x.x.x/standalone_examples
# - Windows: %userprofile%\AppData\Local\ov\pkg\isaac_sim-x.x.x\standalone_examples
# - Container: /isaac-sim/standalone_examples

# Import and launch the Omniverse Toolkit before any other imports.
# Note: Omniverse loads various plugins at runtime which
# cannot be imported unless the Toolkit is already running.
from isaacsim import SimulationApp


# Parse any command-line arguments specific to the standalone application
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test-arg", type=str, default="test", help="Test argument.")
# Parse only known arguments, so that any (eg) Kit settings are passed through to the core Kit app
args, _ = parser.parse_known_args()

# See DEFAULT_LAUNCHER_CONFIG for available configuration
# https://docs.omniverse.nvidia.com/py/isaacsim/source/extensions/omni.isaac.kit/docs/index.html
launch_config = {"headless": True}
# Launch the Toolkit
simulation_app = SimulationApp(launch_config)


# Locate any other import statement after this point
import omni
import platform
import numpy as np
import cv2

from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
from isaacsim.core.api.objects import DynamicCuboid
from pxr import UsdGeom, Gf, UsdPhysics, Usd, UsdLux, Sdf
from isaacsim.core.api.world import World
from isaacsim.core.api.simulation_context import SimulationContext
from isaacsim.sensors.camera import Camera
import omni.isaac.core.utils.prims as prim_utils

world = World()
simulation_context = SimulationContext()


ROBOT_LINUX_PATH = "/home/jonas/isaac_sim_model/xarm7_with_gripper.usd"
ROBOT_WINDOWS_PATH = "F:\\GitRepos\\isaac_sim\\xarm7.usd"
ROBOT_PATH = ""

DESK_LINUX_PATH = "/home/jonas/isaac_sim_model/desk.usd"
DESK_WINDOWS_PATH = "F:\\GitRepos\\isaac_sim\\desk.usd"
DESK_PATH = ""

if platform.system()=="Linux":
    ROBOT_PATH = ROBOT_LINUX_PATH
    DESK_PATH = DESK_LINUX_PATH
elif platform.system()=="Windows":
    ROBOT_PATH = ROBOT_WINDOWS_PATH
    DESK_PATH = DESK_WINDOWS_PATH


world.scene.add_default_ground_plane()
asset_path = DESK_PATH
add_reference_to_stage(usd_path=asset_path, prim_path="/World/Desk")
asset_path = ROBOT_PATH   

light_1 = prim_utils.create_prim(
    "/World/SphereLight",
    "SphereLight",
    position=np.array([1.0, 1.0, 5.0]),
    attributes={
        "inputs:radius": 0.01,
        "inputs:intensity": 5e4,  # High intensity typically needed
        "inputs:color": (1.0, 1.0, 1.0)
    }
)

cube = world.scene.add(
DynamicCuboid(
    prim_path="/World/random_cube", # The prim path of the cube in the USD stage
    name="cube", # The unique name used to retrieve the object from the scene later on
    position=np.array([0, 0, 1.0]), # Using the current stage units which is in meters by default.
    scale=np.array([0.05, 0.05, 0.05]), # most arguments accept mainly numpy arrays.
    color=np.array([0, 0, 1.0]), # RGB channels, going from 0-1
    mass=0.1,
))

# Add robot 1
robot_prim_path = "/World/Robot_01"
default_joints = np.array([0.0, -45, 0.0, 45, 0.0, 90, 0.0])
add_reference_to_stage(usd_path=asset_path, prim_path=robot_prim_path)
stage = world.stage
prim = stage.GetPrimAtPath(robot_prim_path)
xform = UsdGeom.Xformable(prim)
xform.ClearXformOpOrder() 
xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.555, 0.8125))
xform.AddOrientOp().Set(Gf.Quatf(0.7071068, 0.0, 0.0, -0.7071068))
# calc inverse matrix of robot base for later use
base_mat = xform.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
robot_01_prim_matrix_inverse = base_mat.GetInverse()
# set default joint positions
base_joint_path = "/World/Robot_01/xarm7/joints" 
for i, angle in enumerate(default_joints):
    joint_index = i + 1
    joint_path = f"{base_joint_path}/joint{joint_index}"
    joint_prim = stage.GetPrimAtPath(joint_path)
    if joint_prim.IsValid():
        joint_state = UsdPhysics.Joint(joint_prim)
        val_attr = joint_prim.GetAttribute("state:angular:physics:position")
        if val_attr:
            val_attr.Set(float(angle))
    else:
        print(f"Warning: Could not find joint at {joint_path}")
robot_01 = world.scene.add(
    Robot(
        prim_path="/World/Robot_01/xarm7",
        name="robot_01",
        )
)

# Add robot 2
robot_prim_path = "/World/Robot_02"
default_joints = np.array([0.0, -45, 0.0, 45, 0.0, 90, 0.0])
add_reference_to_stage(usd_path=asset_path, prim_path=robot_prim_path)
stage = world.stage
prim = stage.GetPrimAtPath(robot_prim_path)
xform = UsdGeom.Xformable(prim)
xform.ClearXformOpOrder() 
xform.AddTranslateOp().Set(Gf.Vec3d(0.0, -0.545, 0.8125))
xform.AddOrientOp().Set(Gf.Quatf(0.7071068, 0.0, 0.0, 0.7071068))
base_joint_path = "/World/Robot_02/xarm7/joints" 
for i, angle in enumerate(default_joints):
    joint_index = i + 1
    joint_path = f"{base_joint_path}/joint{joint_index}"
    joint_prim = stage.GetPrimAtPath(joint_path)
    if joint_prim.IsValid():
        joint_state = UsdPhysics.Joint(joint_prim)
        val_attr = joint_prim.GetAttribute("state:angular:physics:position")
        if val_attr:
            val_attr.Set(float(angle))
    else:
        print(f"Warning: Could not find joint at {joint_path}")
robot_02 = world.scene.add(
    Robot(
        prim_path="/World/Robot_02/xarm7", 
        name="robot_02",
        )
)

cam_wrist_right = Camera(prim_path="/World/Robot_01/xarm7/link7/link_eef/wrist_cam",
                         resolution=(640, 480))
cam_wrist_left  = Camera(prim_path="/World/Robot_02/xarm7/link7/link_eef/wrist_cam",
                         resolution=(640, 480))
cam_top_view  = Camera(prim_path="/World/Desk/Desk/top_view_cam",
                         resolution=(640, 480))

cam_wrist_right.initialize()
cam_wrist_left.initialize()
cam_top_view.initialize()


simulation_context.play()

while True:
    simulation_app.update()

    # 2. Get the RGB data
    rgb_data = cam_top_view.get_rgb()
    
    if rgb_data is not None:
        # 3. Convert RGB (Isaac) to BGR (OpenCV)
        # Note: rgb_data is a numpy array
        bgr_frame = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
        
        # 4. Display the frame
        cv2.imshow("Wrist Camera Left", bgr_frame)
        
        # 5. Required to refresh the window and allow 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cv2.destroyAllWindows()
simulation_app.close()

