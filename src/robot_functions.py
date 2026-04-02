from isaacsim.core.utils.types import ArticulationAction
import numpy as np

def get_joints(robot):
    joints_robot = robot.get_joint_positions()
    joints_robot[7]=0.85-joints_robot[7]
    return joints_robot[:8]


def set_joints(robot, joints):
    copied_joints = joints.copy()
    copied_joints[-1]= 0.85 - copied_joints[-1]
    action = ArticulationAction(joint_positions=copied_joints, joint_indices=np.array([0,1,2,3,4,5,6,7]))
    robot.apply_action(control_actions=action)