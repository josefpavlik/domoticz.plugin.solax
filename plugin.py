# SELV
#
# Author: Jet 2023
# based on HTML.py example
#
#
"""
<plugin key="solax" name="solax" author="Jet" version="0.1" externallink="">
    <description>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Port" label="Port" width="75px" default="80"/>
        <param field="Mode1" label="Password" width="100px" default=""/>
        <param field="Mode2" label="Device name" width="75px" default=""/>
        <param field="Mode4" label="Polling period [s]" width="75px" default="3"/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import json
import Domoticz
import os
import re 

class BasePlugin:
    httpConn = None
    runAgain = 1
    disconnectCount = 0
    devices=[
        (0,"L1 Voltage","V",0.1,"%.1f"),
        (1,"L2 Voltage","V",0.1,"%.1f"),
        (2,"L3 Voltage","V",0.1,"%.1f"),
        ]
    xdevices=[
        (0,"Grid Voltage L1","V",0.1,"%.1f"),
        (1,"Grid Voltage L2","V",0.1,"%.1f"),
        (2,"Grid Voltage L3","V",0.1,"%.1f"),
        (3,"Output Current L1","A",0.1,"%.1f"),
        (4,"Output Current L2","A",0.1,"%.1f"),
        (5,"Output Current L3","A",0.1,"%.1f"),
        (6,"Output Power L1","W",1,"%d"),
        (7,"Output Power L2","W",1,"%d"),
        (8,"Output Power L3","W",1,"%d"),
        (9,"PV1 Voltage","V",0.1,"%.1f"),
        (10,"PV2 Voltage","V",0.1,"%.1f"),
        (11,"PV1 Current","A",0.1,"%.1f"),
        (12,"PV2 Current","A",0.1,"%.1f"),
        (13,"PV1 Power","W",1,"%d"),
        (14,"PV2 Power","W",1,"%d"),
        (15,"Grid Frequency L1","Hz",0.01,"%.2f"),
        (16,"Grid Frequency L2","Hz",0.01,"%.2f"),
        (17,"Grid Frequency L3","Hz",0.01,"%.2f"),
        (181,"AC Output Power","W",1,"%d"),
        (19,"Energy Total","kWh",1,"%d"),
        (21,"Energy Today","kWh",0.1,"%.1f"),
        (24,"Battery Voltage","V",0.01,"%.2f"),
        (25,"Battery Current","A",0.01,"%.2f"),
        (26,"Battery Power","W",1,"%d"),
        (27,"Battery Temperature","C",0.1,"%.1f"),
        (28,"Battery Capacity","%",1,"%d"),
        (32,"Battery Remaining","kWh",0.1,"%.1f"),
        (67,"Total Feed-in Energy","kWh",1,"%d"),
        (69,"Total Consumption","kWh",1,"%d"),
    ]
   
    def __init__(self):
        return

    def connection(self):
        return Domoticz.Connection(Name="ReadRealtimeData", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
      
    def onStart(self):        
        Domoticz.Log("onStart - solax Plugin is starting.")
        self.password = Parameters["Mode1"]
        devname = Parameters["Mode2"]
        self.period=int(Parameters["Mode4"])
        Domoticz.Heartbeat(self.period)
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        for (unit,name,type,mul,formt) in self.devices:
            fullname= devname+" "+name if devname else name
            Domoticz.Debug("creating device %d %s" % (unit, fullname))
            Domoticz.Device(fullname, Unit=unit+1, TypeName="Custom", Used=1).Create()


    def onStop(self):
        Domoticz.Log("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Log("solax connected successfully.")
            data=[
                "optType=ReadRealTimeData",
                "pwd="+self.password,
            ]
            data_stream="&".join(data)
            """
            hdr=[
                "POST / HTTP/1.1",
                "Content-Type: application/x-www-form-urlencoded",
                "Content-Length: %d" % len(data_stream)
            ]
            request="\r\n".join(hdr)+"\r\n\r\n"+data_stream
            Domoticz.Log("solax send request "+request)
            Connection.Send(request)
"""
            request = { 'Verb' : 'POST',
                'URL'  : '/',
                'Headers' : { 
                    'Content-Type' : 'application/x-www-form-urlencoded',
                    'Connection': 'keep-alive',
                    'Accept': 'Content-Type: text/html; charset=UTF-8',
                    'Host': Parameters["Address"]+":"+Parameters["Port"],
                    'User-Agent': 'Domoticz/1.0' 
                    },
                'Data' : data_stream
            }
            Connection.Send(request)

        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Mode1"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
#        DumpHTTPResponseToLog(Data)
        
        strData = Data["Data"].decode("utf-8", "ignore")
        Status = int(Data["Status"])
        if (Status == 200):
            if ((self.disconnectCount & 1) == 1):
#                Domoticz.Log("Good Response received from selv, Disconnecting.")
#                self.httpConn.Disconnect()
                unused=0
            else:
#                Domoticz.Log("Good Response received from selv, Dropping connection.")
                self.httpConn = None
            self.disconnectCount = self.disconnectCount + 1
# parse result        
            Domoticz.Log("data="+strData)
            res = json.loads(strData)
#            Domoticz.Log("dump: "+json.dumps(res))
            reg = res['Data']
            for (unit,name,type,mul,format) in self.devices:
                val=reg[unit]*mul
                Domoticz.Log("solax device %d = %f" % (unit,val))
                Devices[unit+1].Update(0,format % val, Options={'Custom': '1;'+type} )
        elif (Status == 400):
            Domoticz.Error("selv returned a Bad Request Error.")
        elif (Status == 500):
            Domoticz.Error("selv returned a Server Error.")
        else:
            Domoticz.Error("selv returned a status: "+str(Status))

    def update_lights(self, lights):
        for i in range(0,self.channels):
            self.update_light(i+1, lights[i]=='1')
            
    def update_light(self, Unit, state):
        val=state and "1" or "0"
#        if (Unit in Devices): Devices[Unit].Update(int(val),val)
    
    def onCommand(self, Unit, Command, Level, Hue):
        cmd=Command=="On" and "G" or "g"
        command="curl http://"+Parameters["Address"]+":"+Parameters["Port"]+"/"+self.pin+"p"+str(Unit-1)+cmd+" &"
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + " exec "+command)
#        os.system(command)
#        Domoticz.Debug("done")
#        self.update_light(Unit, Command=="On")

    def onDisconnect(self, Connection):
        unused=0
#        Domoticz.Log("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        self.httpConn = self.connection()
        self.httpConn.Connect()
                 
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def LogMessage(Message):
    if Parameters["Mode6"] == "File":
        f = open(Parameters["HomeFolder"]+"http.html","w")
        f.write(Message)
        f.close()
        Domoticz.Log("File written")

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("--->'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Debug("------->'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("--->'" + x + "':'" + str(httpDict[x]) + "'")
