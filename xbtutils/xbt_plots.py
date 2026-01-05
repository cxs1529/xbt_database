import matplotlib.pyplot as plt

# Only for testing purposes
def plot_profile(depth, temperature):
    fig, ax = plt.subplots()  
    ax.plot(temperature, depth)
    ax.set_xlabel("Temperature [C]")
    ax.set_ylabel("Depth [m]")
    plt.show()


