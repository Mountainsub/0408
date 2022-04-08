
import pandas as pd
import numpy as np
import time 
import sys
import os
import ctypes
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import datetime

from lib.ddeclient import DDEClient
from price_logger import ClientHolder 
from price_logger import LastNPerfTime
from init import keisan

class plot_time:
    def __init__(self):
        self.hdffilename = "./data/sum.hdf5"
        self.store = pd.HDFStore(self.hdffilename)
        self.key_name = "testcase" 
        self.key_name2 = "timecase"

    def hozon(self, data_dict):
        #print("OK")
        self.store.append(self.key_name, data_dict)

    def hozon2(self, data_dict):
        #print("OK")
        self.store.append(self.key_name2, data_dict)
      
class up_or_down:
    def __init__(self, calc, topix):
        
        
        self.RED = '\033[31m'
        self.BLUE = '\033[34m'
        self.END = '\033[0m'
        
        #self.switch = switch 
        dif = calc - float(topix)
        if dif > 10 or dif < -10:
            self.Boolean = "repair"
            return
        
        elif  dif >= 0.5:
            self.Boolean = "up"
        elif dif <= -0.5:
            self.Boolean = "down"
        else:
            self.Boolean = "None"
        self.calc = calc
    def judge(self):
        t = self.Boolean
        RED = self.RED
        BLUE = self.BLUE
        END = self.END
        if t == "up":
            string = RED +"計算した値が、実際のTOPIXより高いです。"+END
 
        elif t == "down":
            string = BLUE+"計算した値が、実際のTOPIXより低いです。"+END
        elif t == "repair":
            string = "差が大きすぎる"
        else:
            string = "変化が小さいので手を加えない方がよいでしょう。"
        return string

    def lever(self):
        return self.switch
    


if __name__ == "__main__":
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
    
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    kernel32.SetConsoleMode(handle, MODE)

    t1 = time.time()
    calc = 0
    timer = LastNPerfTime(2**20)
    object_pass = "value"
    dde = DDEClient("rss", "TOPX")
    store_x = pd.HDFStore("./data/sum2.hdf5")
    topix = dde.request("現在値").decode("sjis")
    temp  = store_x.get("consequence")
    calc = float(temp["calc"].tail(1))
    topix = float(topix)
    """
    TOPIX
    （calc:8000 / 初期値）× 100
    初期値
    (calc / TOPIX ) kakeru 100
    
    """
    
    #4/8 8222.883552900003
    
    topix_init = 100 * calc / float(topix)         
    switch = "neutral"
    
    while True:
        
        print(calc, topix)
        holder = plot_time()
        
        timer.start()
        calc = 0
        x = 1
        
        for i in range(18):
            idx = i *126
            filename = "./data/" + str(idx).zfill(3)+ ".hdf5"
             
            try:
                with pd.HDFStore(filename) as store:
                    temp =store.get(object_pass)
            except:
                pass
            else:
                end = temp.tail(1)
                v = float(end["0"])
                if v==0:
                    now = datetime.datetime.now()
                    print(i, "attention", now)
                    """
                    with pd.HDFStore("./data/caution.hdf5") as store:
                        store.append("zero",pd.DataFrame({"caution":[now], "id": [i]})) 
                    """
                    #x += 1
                    #v = float(temp.iat[-1* x,0])
                else:
                    print(i, "pass")
                    x = 1
                calc += v
            
        
        dict = {"total": [calc]}
        timer.end()
                
        series = pd.DataFrame(dict)

        #保存
        holder.hozon(series)
        
        temp = timer.get_sum_time()    
        dict = {"time": [temp]}
        df = pd.DataFrame(dict)
        
        holder.hozon2(df)   
        timer.count_one()
        
        
        now = datetime.datetime.now()
        print(calc)
        calc /= topix_init 
        calc *= 100
        
        topix = dde.request("現在値").decode("sjis")
        
        
        instance = up_or_down(calc, topix)
        
        
        string = instance.judge()
        print("取得時刻:"+str(now),"計算値:" + str(calc), string)
        data_dict = {"time":[now], "calc":[calc], "topix":[topix]}
        #print(data_dict)
        store_x.append("consequence",pd.DataFrame(data_dict), index=False)
        #pre_calc = calc
        #pre_topix = topix
        #switch = instance.lever()
        
        
        if string =="差が大きすぎる":
            topix_init = float(topix_init)* float(calc) / float(topix)
            #1882.4188190928678