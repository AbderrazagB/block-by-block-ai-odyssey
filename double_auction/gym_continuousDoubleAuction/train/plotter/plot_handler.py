import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ray

#from gym_continuousDoubleAuction.train.storage.store_handler import get_lv_data

fig_size = (25,10)
#step_window = 100 #int(np.rint(max_step * 0.1))
#eps_window = 15 #int(np.rint(num_iters * 0.1))

def _window_size(y):
    return int(np.rint(len(y) * 0.1))

def _process_list(init_cash, agt_id, step_or_eps, data_key):
    g_store = ray.get_actor("g_store")
    store = ray.get(g_store.get_storage.remote())
    
    # Handle both string and integer agent IDs
    if isinstance(agt_id, int):
        agt_key = f"agt_{agt_id}"
    else:
        agt_key = agt_id
    
    # Check if key exists in store
    if agt_key not in store:
        print(f"Warning: {agt_key} not found in storage. Available keys: {list(store.keys())}")
        return []
    
    l = store[agt_key][step_or_eps][data_key]
    
    # Debug: print data length
    if len(l) == 0:
        print(f"Warning: No data for {agt_key} -> {step_or_eps} -> {data_key}")
        return []
    
    if step_or_eps == "step":
        l = [item for sublist in l for item in sublist]

    if data_key == "reward":
        l = np.cumsum(l)
        #l = l
    elif data_key == "NAV":
        l = [val - init_cash for val in l]         # cumulative returns
        l = np.cumsum(l)
    elif data_key == "num_trades":
        #l = pd.Series(l).rolling(window=_window_size(l)).mean()
        l = np.cumsum(l)
        #l = l
    else:
        l = []

    return l

def plot_storage(num_agents, init_cash, x_label="eps", ylabel="reward", fig_size=(25, 10)):
    # Create appropriate grid layout for num_agents
    if num_agents <= 4:
        rows, cols = 2, 2
    elif num_agents <= 6:
        rows, cols = 2, 3
    elif num_agents <= 9:
        rows, cols = 3, 3
    elif num_agents <= 12:
        rows, cols = 3, 4
    else:
        sq_rt = np.sqrt(num_agents)
        rows = cols = math.ceil(sq_rt)
    
    num_del = rows * cols - num_agents  # num of unused axes to hide

    fig, axes_array = plt.subplots(rows, cols, figsize=fig_size, sharex=False, sharey=True)
    
    # Flatten axes array for easier indexing
    if num_agents == 1:
        axes = [axes_array]
    else:
        axes = axes_array.flatten()
    
    print(f"\n🎨 Plotting {ylabel} data for {num_agents} agents (x-axis: {x_label})...")
    
    for agt_id in range(num_agents):
        pl = _process_list(init_cash, agt_id, x_label, ylabel)
        if len(pl) > 0:
            axes[agt_id].plot(range(len(pl)), pl, label='agt_'+str(agt_id), color=np.random.uniform(0,1,3))
            axes[agt_id].legend()
            axes[agt_id].set(xlabel=x_label, ylabel=ylabel)
            axes[agt_id].grid(True, alpha=0.3)
        else:
            axes[agt_id].text(0.5, 0.5, f'No data for agent {agt_id}', 
                            ha='center', va='center', transform=axes[agt_id].transAxes)

    # Hide unused axes
    for i in range(num_del):
        axes[-(i+1)].set_axis_off()
    
    plt.tight_layout()
    plt.show()

def plot_LOB_subplot(store, depth, y_label, fig_size=(25,5)):
    #store = [item for sublist in store for item in sublist]
    fig, axs = plt.subplots(depth, figsize=(25,25), sharex=True, sharey=True)
    for i, _ in enumerate(axs):
        x = range(len(store[i]))
        y = store[i]
        axs[i].plot(x, y , color=np.random.uniform(0,1,3))
        axs[i].set(ylabel='lv_' + str(i+1) + y_label)
    axs[i].set(xlabel='step')

def plot_sum_ord_imb(sum_ord_imb_store, y_label, fig_size=(25,5)):
    plt.figure(figsize=fig_size)
    plt.xlabel("step")
    plt.ylabel(y_label)
    x = range(len(sum_ord_imb_store))
    y = sum_ord_imb_store
    plt.plot(x, y, color=np.random.uniform(0,1,3),label=y_label, linewidth=0.7)

    y_MA = pd.Series(y).rolling(window=_window_size(y)).mean()
    plt.plot(x, y_MA, color='black', label='MA', linewidth=1)

    plt.legend()
    plt.show()

def plot_mid_prices(mid_price_store, y_label="mid_prices", fig_size=(25,5)):
    plt.figure(figsize=fig_size)
    plt.xlabel("step")
    plt.ylabel(y_label)
    for i, row in enumerate(mid_price_store):
        x = range(len(row))
        y = row
        plt.plot(x, y, color=np.random.uniform(0,1,3), label="lv_" + str(i+1), linewidth=0.7)

    plt.legend()
    plt.show()
