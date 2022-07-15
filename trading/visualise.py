import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from binance import Client
import pandas as pd
import os

#Config
import sys
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigBinance
conf = ConfigBinance().getKeys()

#Init Binance Client
client = Client(conf[0],conf[1])
asset = "BTCUSDT"

plt.style.use("ggplot")

def getminutedata(symbol,interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms")
    frame = frame.astype(float)
    return frame

def getDateData(symbol,interval, start_str, end_str):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,start_str,end_str))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms",utc=True)
    #frame.index = frame.index.strftime( "%d-%m-%Y  %H:%M")  
    frame = frame.astype(float)
    print(frame.to_string())
    return frame

#Test functions
#df = getminutedata(asset, "1m","120m")
#df = getminutedata(asset,"1m","12 July, 2022 16:00:00")
#df =getDateData(asset,"1m","12 July, 2022 20:00:00","12 July,2022 22:00:00")

def animate(i):
    data = getminutedata(asset,"1m","120m")
    plt.cla()
    plt.plot(data.index,data.Close)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title(asset)
    plt.gcf().autofmt_xdate() #adjust dates 
    plt.tight_layout()

def getSentiment():
    json_path = "sentiment/Json/12-07-2022/btc.json"
    df = pd.read_json(json_path,orient="index")
    df = df.filter(items=["Time","Sentiment Score"])
    #df_unique = df["Time"].unique()
    df["Time"] = pd.to_datetime(df["Time"],utc=True)#,format="%d-%m-%Y %H:%M:%S")
    df["Time"] = df["Time"].strftime("%d-%m-%Y  %H:%M")
    df_mean= df.resample("1T",on="Time").mean()
    newdf = pd.DataFrame(df_mean)
    #print(df_mean)
    return newdf


def livePlot():
    ani = FuncAnimation(plt.gcf(),animate,1000) #updating every second
    #plt.figure(figsize=((10,8)))
    plt.tight_layout()
    plt.show()
    return ani

def getDatePlotWithSentiment():
    data = getDateData(asset,"1m","12 July, 2022 16:00:00","12 July,2022 22:00:00")
    sent = getSentiment()
    plt.figure(figsize=((12,6)))
    #plt.cla()
    ax1 = plt.subplot(121)
    plt.tick_params('x')
    plt.title(f"Price for {asset}")

    plt.plot(data.index,data.Close)
    
    ax2 = plt.subplot(122,label="Sentiment Score2") #,sharex=ax1)
    # make these tick labels invisible
    plt.tick_params('x')   
    plt.title("Sentiment Score")
    plt.plot(sent)#sent.index,sent["Sentiment Score"].values)
    
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

#anim = livePlot()
getDatePlotWithSentiment()