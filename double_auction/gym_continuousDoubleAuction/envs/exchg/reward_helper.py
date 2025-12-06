import numpy as np
import pandas as pd

class Reward_Helper(object):

    def set_reward(self, rewards, trader):
        """
        reward per t step
        reward = nav@t+1 - nav@t
        """

        NAV_chg = float(trader.acc.nav - trader.acc.prev_nav)

        # Simple reward: just maximize NAV change
        # The original penalty for trades was too harsh and caused massive negative rewards
        rewards[trader.ID] = NAV_chg
        
        # Optional: small penalty for excessive trading (much gentler than original)
        # if trader.acc.num_trades > 0:
        #     rewards[trader.ID] -= 0.1 * trader.acc.num_trades

        trader.acc.reward = rewards[trader.ID]

        return rewards
