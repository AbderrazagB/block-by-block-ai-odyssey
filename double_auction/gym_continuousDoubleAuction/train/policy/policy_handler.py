from ray.rllib.policy.policy import Policy
from ray.rllib.utils.typing import TensorType
from ray.rllib.policy.sample_batch import SampleBatch
import numpy as np
import tree

def make_RandomPolicy(_seed):

    class RandomPolicy(Policy):
        """
        A hand-coded policy that returns random actions in the env (doesn't learn).
        """

        def __init__(self, observation_space, action_space, config):
            # Call parent init with proper parameters
            super().__init__(observation_space, action_space, config)
            # Seed the action space
            if hasattr(action_space, 'seed'):
                action_space.seed(_seed)

        def compute_actions_from_input_dict(self, input_dict, **kwargs):
            """Compute actions from input dict - bypasses action processing."""
            obs_batch = input_dict["obs"]
            batch_size = len(obs_batch)
            
            # Sample actions and structure them properly for Tuple space
            # Tuple space: (Discrete(3), Discrete(4), Box(1,), Box(1,), Discrete(12))
            samples = [self.action_space.sample() for _ in range(batch_size)]
            
            # Restructure as separate arrays for each component of the tuple
            # This is what RLlib expects for Tuple action spaces
            if batch_size > 0 and isinstance(samples[0], tuple):
                # Transpose list of tuples into tuple of lists
                actions = tuple(
                    np.array([sample[i] for sample in samples])
                    for i in range(len(samples[0]))
                )
            else:
                actions = samples
            
            return actions, [], {}

        def compute_actions(self,
                            obs_batch,
                            state_batches=None,
                            prev_action_batch=None,
                            prev_reward_batch=None,
                            info_batch=None,
                            episodes=None,
                            **kwargs):
            """Compute actions on a batch of observations."""
            batch_size = len(obs_batch)
            samples = [self.action_space.sample() for _ in range(batch_size)]
            
            # Restructure for Tuple space: convert list of tuples to tuple of arrays
            if batch_size > 0 and isinstance(samples[0], tuple):
                actions = tuple(
                    np.array([sample[i] for sample in samples])
                    for i in range(len(samples[0]))
                )
            else:
                actions = samples
            
            return actions, [], {}

        def compute_single_action(self, obs, state=None, **kwargs):
            """Compute a single action (called per-agent in some cases)."""
            return self.action_space.sample(), [], {}

        def learn_on_batch(self, samples):
            """No learning."""
            return {}

        def get_weights(self):
            return {}

        def set_weights(self, weights):
            pass

    return RandomPolicy

def gen_policy(i, obs_space, act_space):
    """
    Each policy can have a different configuration (including custom model)
    """

    config = {
        "model": {"custom_model": "model_disc"},
        "gamma": 0.99,
        "lr": 5e-5,  # Learning rate must be set as float
    }
    return (None, obs_space, act_space, config)

def set_agents_policies(policies, obs_space, act_space, num_agents, num_trained_agent):
    """
    Set 1st policy as PPO & override all other policies as RandomPolicy with
    different seed.
    """

    # set all agents to use random policy
    for i in range(num_agents):
        policies["policy_{}".format(i)] = (make_RandomPolicy(i), obs_space, act_space, {})

    # set trained agents to use None (PPOTFPolicy)
    for i in range(num_trained_agent):
        #policies["policy_{}".format(i)] = (PPOTFPolicy, obs_space, act_space, {})
        policies["policy_{}".format(i)] = (None, obs_space, act_space, {})

    print('policies:', policies)
    return 0

def create_train_policy_list(num_trained_agent, prefix):
    """
    Storage for train_policy_list for declaring train poilicies in trainer config.
    """
    
    storage = []
    for i in range(0, num_trained_agent):
        storage.append(prefix + str(i))

    print("train_policy_list = ", storage)
    return storage
