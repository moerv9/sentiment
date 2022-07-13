import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from binance import Client
import pandas as pd

#Config
import sys
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigBinance
conf = ConfigBinance().getKeys()

client = Client(conf[0],conf[1])

plt.style.use("ggplot")
print(plt.style.available)