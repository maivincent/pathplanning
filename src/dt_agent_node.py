#!/usr/bin/env python

import rospy
from std_msgs.msg import Float32MultiArray
from pathplan_uncertainty.msg import Pose2DTimeStep, Observation, AgentCommand
from pathplan_uncertainty.srv import GroundType
from dt_agent.agent import Agent

class AgentNode(object):
    def __init__(self):  

        # Parameters 

        ## Agent parameters
        self.time_horizon = rospy.get_param("/agent/planner/time_horizon")
        self.vel_resolution = rospy.get_param("/agent/planner/vel_resolution")
        self.y_resolution = rospy.get_param("/agent/planner/y_resolution")
        self.y_horizon = rospy.get_param("/agent/planner/y_horizon")
        self.comp_time_mean = rospy.get_param("/agent/computation_time/mean")
        self.comp_time_std_dev = rospy.get_param("/agent/computation_time/std_dev")        
        self.agent_params = {"time_horizon": self.time_horizon, "vel_resolution": self.vel_resolution, "y_resolution": self.y_resolution, "y_horizon": self.y_horizon, "comp_time_mean": self.comp_time_mean, "comp_time_std_dev": self.comp_time_std_dev}

        ## Sim parameters
        self.dt = rospy.get_param("/sim/dt")
        self.road_width = rospy.get_param("/sim/world/road/width")
        self.other_duckie_type = rospy.get_param("/sim/other_duckie_type")
        self.other_duckie_max_acceleration = rospy.get_param("/duckiebots/" + self.other_duckie_type + "/max_acceleration")
        self.other_duckie_max_velocity = rospy.get_param("/duckiebots/" + self.other_duckie_type + "/max_velocity")
        self.sim_params = {"dt": self.dt, "road_width": self.road_width, "other_duckie_type": self.other_duckie_type, "other_duckie_max_acceleration": self.other_duckie_max_acceleration, "other_duckie_max_velocity": self.other_duckie_max_velocity}

        #Publishers
        self.pub_agent_command = rospy.Publisher("/agent/command", AgentCommand, queue_size = 5)

        # Subscribers
        self.sub_observations = rospy.Subscriber("/sim/obs/observations", Observation, self.observation_cb)
        
        # Agent
        self.agent = Agent(self.agent_params, self.sim_params)


        rospy.loginfo("[AgentNode] Initialized.")

        rospy.sleep(1)

        rospy.loginfo("[AgentNode] Starting the process.")
        self.start_process()



    def observation_cb(self, obs_msg):
        self.compute_our_plan(obs_msg)


    def compute_our_plan(self, obs_msg):
        time = obs_msg.our_duckie_pose.time
        rospy.loginfo("[AgentNode] Compute our plan at time " + str(time))

        plan, timesteps = self.agent.compute_our_plan(obs_msg)

        self.publish_plan(plan, timesteps)

    def publish_plan(self, plan, timesteps):
        command_msg = AgentCommand()

        plan_msg = Float32MultiArray()
        plan_msg.data = plan
        command_msg.orientation_seq = plan_msg

        command_msg.computation_time_steps = timesteps

        self.pub_agent_command.publish(command_msg)

    def start_process(self):
        plan = []
        timesteps = 1

        self.publish_plan(plan, timesteps)


    def onShutdown(self):
        rospy.loginfo("[AgentNode] Shutdown.")


if __name__ == '__main__':
    rospy.init_node('agent_node',anonymous=False)
    agent_node = AgentNode()
    rospy.on_shutdown(agent_node.onShutdown)
    rospy.spin()