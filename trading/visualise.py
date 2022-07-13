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




asset = "BTCUSDT"

def getminutedata(symbol,interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit = "ms")
    frame = frame.astype(float)
    return frame

df = getminutedata(asset, "1m","120m")

def animate(i):
    data = getminutedata(asset,"1m","120m")
    #plt.figure(figsize=((10,8)))
    plt.cla()
    plt.plot(data.index,data.Close)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title(asset)
    plt.gcf().autofmt_xdate() #adjust dates 
    plt.tight_layout()
    
def getPlot():
    ani = FuncAnimation(plt.gcf(),animate,1000) #updating every second
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=((10,8)))
    plt.tight_layout()
    plt.show()
    return ani

anim = getPlot()