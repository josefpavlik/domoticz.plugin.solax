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
        (0,"Grid Voltage L1","Voltage",0.1,"%.1f"),
        (1,"Grid Voltage L2","Voltage",0.1,"%.1f"),
        (2,"Grid Voltage L2","Voltage",0.1,"%.1f"),
        (3,"Output Current L1","Current (Single)",0.1,"%.1f"),
        (4,"Output Current L2","Current (Single)",0.1,"%.1f"),
        (5,"Output Current L3","Current (Single)",0.1,"%.1f"),
        (6,"Output Power L1","Usage",1,"%d"),
        (7,"Output Power L2","Usage",1,"%d"),
        (8,"Output Power L3","Usage",1,"%d"),
        (9,"AC Output Power","Usage",1,"%d"),
        (10,"PV1 Voltage","Voltage",0.1,"%.1f"),
        (11,"PV2 Voltage","Voltage",0.1,"%.1f"),
        (12,"PV1 Current","Current (Single)",0.1,"%.1f"),
        (13,"PV2 Current","Current (Single)",0.1,"%.1f"),
        (14,"PV1 Power","Usage",1,"%d"),
        (15,"PV2 Power","Usage",1,"%d"),
        (16,"Grid Frequency","Custom:Hz",0.01,"%.2f"),
#        (17,"Grid Frequency L2","Custom:Hz",0.01,"%.2f"),
#        (18,"Grid Frequency L3","Custom:Hz",0.01,"%.2f"),
        (46,"Solax system temperature 1","Temperature",1,"%d"),
        (47,"Feed-in power","Usage",1,"%d"),
        (54,"Solax system temperature 1","Temperature",1,"%d"),
        (68,"Energy week?","kWh",0.1,"0;%.1f"),
        (70,"Energy today","kWh",0.1,"0;%.1f"),
        (80,"Energy2 week?","kWh",0.1,"0;%.1f"),
        (82,"Energy2 today","kWh",0.1,"0;%.1f"),
        (86,"Energy from grid / month","kWh",0.1,"0;%.1f"),
        (88,"Energy from grid","kWh",0.1,"0;%.1f"),
        (90,"Feed-in energy today","kWh",0.1,"0;%.1f"),
        (92,"Energy from grid today","kWh",0.1,"0;%.1f"),


        (19,"Unknown 19","Custom:??",1,"%d"),
        (20,"Unknown 20","Custom:??",1,"%d"),
        (21,"Unknown 21","Custom:??",1,"%d"),
        (22,"Unknown 22","Custom:??",1,"%d"),
        (23,"Unknown 23","Custom:??",1,"%d"),
        (24,"Unknown 24","Custom:??",1,"%d"),
        (25,"Unknown 25","Custom:??",1,"%d"),
        (26,"Unknown 26","Custom:??",1,"%d"),
        (27,"Unknown 27","Custom:??",1,"%d"),
        (28,"Unknown 28","Custom:??",1,"%d"),
        (29,"Unknown 29","Custom:??",1,"%d"),
        (30,"Unknown 30","Custom:??",1,"%d"),
        (31,"Unknown 31","Custom:??",1,"%d"),
        (32,"Unknown 32","Custom:??",1,"%d"),
        (33,"Unknown 33","Custom:??",1,"%d"),
        (34,"Unknown 34","Custom:??",1,"%d"),
        (35,"Unknown 35","Custom:??",1,"%d"),
        (36,"Unknown 36","Custom:??",1,"%d"),
        (37,"Unknown 37","Custom:??",1,"%d"),
        (38,"Unknown 38","Custom:??",1,"%d"),
        (39,"Unknown 39","Custom:??",1,"%d"),
        (40,"Unknown 40","Custom:??",1,"%d"),
        (41,"Unknown 41","Custom:??",1,"%d"),
        (42,"Unknown 42","Custom:??",1,"%d"),
        (43,"Unknown 43","Custom:??",1,"%d"),
        (44,"Unknown 44","Custom:??",1,"%d"),
        (45,"Unknown 45","Custom:??",1,"%d"),
        (48,"Unknown 48","Custom:??",1,"%d"),
        (49,"Unknown 49","Custom:??",1,"%d"),
        (50,"Unknown 50","Custom:??",1,"%d"),
        (51,"Unknown 51","Custom:??",1,"%d"),
        (52,"Unknown 52","Custom:??",1,"%d"),
        (53,"Unknown 53","Custom:??",1,"%d"),
        (55,"Unknown 55","Custom:??",1,"%d"),
        (56,"Unknown 56","Custom:??",1,"%d"),
        (57,"Unknown 57","Custom:??",1,"%d"),
        (58,"Unknown 58","Custom:??",1,"%d"),
        (59,"Unknown 59","Custom:??",1,"%d"),
        (60,"Unknown 60","Custom:??",1,"%d"),
        (61,"Unknown 61","Custom:??",1,"%d"),
        (62,"Unknown 62","Custom:??",1,"%d"),
        (63,"Unknown 63","Custom:??",1,"%d"),
        (64,"Unknown 64","Custom:??",1,"%d"),
        (65,"Unknown 65","Custom:??",1,"%d"),
        (66,"Unknown 66","Custom:??",1,"%d"),
        (67,"Unknown 67","Custom:??",1,"%d"),
        (69,"Unknown 69","Custom:??",1,"%d"),
        (71,"Unknown 71","Custom:??",1,"%d"),
        (72,"Unknown 72","Custom:??",1,"%d"),
        (73,"Unknown 73","Custom:??",1,"%d"),
        (74,"Unknown 74","Custom:??",1,"%d"),
        (75,"Unknown 75","Custom:??",1,"%d"),
        (76,"Unknown 76","Custom:??",1,"%d"),
        (77,"Unknown 77","Custom:??",1,"%d"),
        (78,"Unknown 78","Custom:??",1,"%d"),
        (79,"Unknown 79","Custom:??",1,"%d"),
        (81,"Unknown 81","Custom:??",1,"%d"),
        (83,"Unknown 83","Custom:??",1,"%d"),
        (84,"Unknown 84","Custom:??",1,"%d"),
        (85,"Unknown 85","Custom:??",1,"%d"),
        (87,"Unknown 87","Custom:??",1,"%d"),
        (89,"Unknown 89","Custom:??",1,"%d"),
        (91,"Unknown 91","Custom:??",1,"%d"),
        (93,"Unknown 93","Custom:??",1,"%d"),
        (94,"Unknown 94","Custom:??",1,"%d"),
        (95,"Unknown 95","Custom:??",1,"%d"),
        (96,"Unknown 96","Custom:??",1,"%d"),
        (97,"Unknown 97","Custom:??",1,"%d"),
        (98,"Unknown 98","Custom:??",1,"%d"),
        (99,"Unknown 99","Custom:??",1,"%d"),
        (100,"Unknown 100","Custom:??",1,"%d"), 
        (101,"Unknown 101","Custom:??",1,"%d"),
        (102,"Unknown 102","Custom:??",1,"%d"),
        """ 
        (103,"Unknown 103","Custom:??",1,"%d"), # all zeroes, only 167-170 are 257
        (104,"Unknown 104","Custom:??",1,"%d"),
        (105,"Unknown 105","Custom:??",1,"%d"),
        (106,"Unknown 106","Custom:??",1,"%d"),
        (107,"Unknown 107","Custom:??",1,"%d"),
        (108,"Unknown 108","Custom:??",1,"%d"),
        (109,"Unknown 109","Custom:??",1,"%d"),
        (110,"Unknown 110","Custom:??",1,"%d"),
        (111,"Unknown 111","Custom:??",1,"%d"),
        (112,"Unknown 112","Custom:??",1,"%d"),
        (113,"Unknown 113","Custom:??",1,"%d"),
        (114,"Unknown 114","Custom:??",1,"%d"),
        (115,"Unknown 115","Custom:??",1,"%d"),
        (116,"Unknown 116","Custom:??",1,"%d"),
        (117,"Unknown 117","Custom:??",1,"%d"),
        (118,"Unknown 118","Custom:??",1,"%d"),
        (119,"Unknown 119","Custom:??",1,"%d"),
        (120,"Unknown 120","Custom:??",1,"%d"),
        (121,"Unknown 121","Custom:??",1,"%d"),
        (122,"Unknown 122","Custom:??",1,"%d"),
        (123,"Unknown 123","Custom:??",1,"%d"),
        (124,"Unknown 124","Custom:??",1,"%d"),
        (125,"Unknown 125","Custom:??",1,"%d"),
        (126,"Unknown 126","Custom:??",1,"%d"),
        (127,"Unknown 127","Custom:??",1,"%d"),
        (128,"Unknown 128","Custom:??",1,"%d"),
        (129,"Unknown 129","Custom:??",1,"%d"),
        (130,"Unknown 130","Custom:??",1,"%d"),
        (131,"Unknown 131","Custom:??",1,"%d"),
        (132,"Unknown 132","Custom:??",1,"%d"),
        (133,"Unknown 133","Custom:??",1,"%d"),
        (134,"Unknown 134","Custom:??",1,"%d"),
        (135,"Unknown 135","Custom:??",1,"%d"),
        (136,"Unknown 136","Custom:??",1,"%d"),
        (137,"Unknown 137","Custom:??",1,"%d"),
        (138,"Unknown 138","Custom:??",1,"%d"),
        (139,"Unknown 139","Custom:??",1,"%d"),
        (140,"Unknown 140","Custom:??",1,"%d"),
        (141,"Unknown 141","Custom:??",1,"%d"),
        (142,"Unknown 142","Custom:??",1,"%d"),
        (143,"Unknown 143","Custom:??",1,"%d"),
        (144,"Unknown 144","Custom:??",1,"%d"),
        (145,"Unknown 145","Custom:??",1,"%d"),
        (146,"Unknown 146","Custom:??",1,"%d"),
        (147,"Unknown 147","Custom:??",1,"%d"),
        (148,"Unknown 148","Custom:??",1,"%d"),
        (149,"Unknown 149","Custom:??",1,"%d"),
        (150,"Unknown 150","Custom:??",1,"%d"),
        (151,"Unknown 151","Custom:??",1,"%d"),
        (152,"Unknown 152","Custom:??",1,"%d"),
        (153,"Unknown 153","Custom:??",1,"%d"),
        (154,"Unknown 154","Custom:??",1,"%d"),
        (155,"Unknown 155","Custom:??",1,"%d"),
        (156,"Unknown 156","Custom:??",1,"%d"),
        (157,"Unknown 157","Custom:??",1,"%d"),
        (158,"Unknown 158","Custom:??",1,"%d"),
        (159,"Unknown 159","Custom:??",1,"%d"),
        (160,"Unknown 160","Custom:??",1,"%d"),
        (161,"Unknown 161","Custom:??",1,"%d"),
        (162,"Unknown 162","Custom:??",1,"%d"),
        (163,"Unknown 163","Custom:??",1,"%d"),
        (164,"Unknown 164","Custom:??",1,"%d"),
        (165,"Unknown 165","Custom:??",1,"%d"),
        (166,"Unknown 166","Custom:??",1,"%d"),
        (167,"Unknown 167","Custom:??",1,"%d"), # 257
        (168,"Unknown 168","Custom:??",1,"%d"), # 257
        (169,"Unknown 169","Custom:??",1,"%d"), # 257
        (170,"Unknown 170","Custom:??",1,"%d"), # 257
        (171,"Unknown 171","Custom:??",1,"%d"),
        (172,"Unknown 172","Custom:??",1,"%d"),
        (173,"Unknown 173","Custom:??",1,"%d"),
        (174,"Unknown 174","Custom:??",1,"%d"),
        (175,"Unknown 175","Custom:??",1,"%d"),
        (176,"Unknown 176","Custom:??",1,"%d"),
        (177,"Unknown 177","Custom:??",1,"%d"),
        (178,"Unknown 178","Custom:??",1,"%d"),
        (179,"Unknown 179","Custom:??",1,"%d"),
        (180,"Unknown 180","Custom:??",1,"%d"),
        (181,"Unknown 181","Custom:??",1,"%d"),
        (182,"Unknown 182","Custom:??",1,"%d"),
        (183,"Unknown 183","Custom:??",1,"%d"),
        (184,"Unknown 184","Custom:??",1,"%d"),
        (185,"Unknown 185","Custom:??",1,"%d"),
        (186,"Unknown 186","Custom:??",1,"%d"),
        (187,"Unknown 187","Custom:??",1,"%d"),
        (188,"Unknown 188","Custom:??",1,"%d"),
        (189,"Unknown 189","Custom:??",1,"%d"),
        (190,"Unknown 190","Custom:??",1,"%d"),
        (191,"Unknown 191","Custom:??",1,"%d"),
        (192,"Unknown 192","Custom:??",1,"%d"),
        (193,"Unknown 193","Custom:??",1,"%d"),
        (194,"Unknown 194","Custom:??",1,"%d"),
        (195,"Unknown 195","Custom:??",1,"%d"),
        (196,"Unknown 196","Custom:??",1,"%d"),
        (197,"Unknown 197","Custom:??",1,"%d"),
        (198,"Unknown 198","Custom:??",1,"%d"),
        (199,"Unknown 199","Custom:??",1,"%d"),
        (200,"Unknown 200","Custom:??",1,"%d"),
        (201,"Unknown 201","Custom:??",1,"%d"),
        (202,"Unknown 202","Custom:??",1,"%d"),
        (203,"Unknown 203","Custom:??",1,"%d"),
        (204,"Unknown 204","Custom:??",1,"%d"),
        (205,"Unknown 205","Custom:??",1,"%d"),
        (206,"Unknown 206","Custom:??",1,"%d"),
        (207,"Unknown 207","Custom:??",1,"%d"),
        (208,"Unknown 208","Custom:??",1,"%d"),
        (209,"Unknown 209","Custom:??",1,"%d"),
        (210,"Unknown 210","Custom:??",1,"%d"),
        (211,"Unknown 211","Custom:??",1,"%d"),
        (212,"Unknown 212","Custom:??",1,"%d"),
        (213,"Unknown 213","Custom:??",1,"%d"),
        (214,"Unknown 214","Custom:??",1,"%d"),
        (215,"Unknown 215","Custom:??",1,"%d"),
        (216,"Unknown 216","Custom:??",1,"%d"),
        (217,"Unknown 217","Custom:??",1,"%d"),
        (218,"Unknown 218","Custom:??",1,"%d"),
        (219,"Unknown 219","Custom:??",1,"%d"),
        (220,"Unknown 220","Custom:??",1,"%d"),
        (221,"Unknown 221","Custom:??",1,"%d"),
        (222,"Unknown 222","Custom:??",1,"%d"),
        (223,"Unknown 223","Custom:??",1,"%d"),
        (224,"Unknown 224","Custom:??",1,"%d"),
        (225,"Unknown 225","Custom:??",1,"%d"),
        (226,"Unknown 226","Custom:??",1,"%d"),
        (227,"Unknown 227","Custom:??",1,"%d"),
        (228,"Unknown 228","Custom:??",1,"%d"),
        (229,"Unknown 229","Custom:??",1,"%d"),
        (230,"Unknown 230","Custom:??",1,"%d"),
        (231,"Unknown 231","Custom:??",1,"%d"),
        (232,"Unknown 232","Custom:??",1,"%d"),
        (233,"Unknown 233","Custom:??",1,"%d"),
        (234,"Unknown 234","Custom:??",1,"%d"),
        (235,"Unknown 235","Custom:??",1,"%d"),
        (236,"Unknown 236","Custom:??",1,"%d"),
        (237,"Unknown 237","Custom:??",1,"%d"),
        (238,"Unknown 238","Custom:??",1,"%d"),
        (239,"Unknown 239","Custom:??",1,"%d"),
        (240,"Unknown 240","Custom:??",1,"%d"),
        (241,"Unknown 241","Custom:??",1,"%d"),
        (242,"Unknown 242","Custom:??",1,"%d"),
        (243,"Unknown 243","Custom:??",1,"%d"),
        (244,"Unknown 244","Custom:??",1,"%d"),
        (245,"Unknown 245","Custom:??",1,"%d"),
        (246,"Unknown 246","Custom:??",1,"%d"),
        (247,"Unknown 247","Custom:??",1,"%d"),
        (248,"Unknown 248","Custom:??",1,"%d"),
        (249,"Unknown 249","Custom:??",1,"%d"),
        (250,"Unknown 250","Custom:??",1,"%d"),
        (251,"Unknown 251","Custom:??",1,"%d"),
        (252,"Unknown 252","Custom:??",1,"%d"),
        (253,"Unknown 253","Custom:??",1,"%d"),
        (254,"Unknown 254","Custom:??",1,"%d")
  """

        ]
#    devices=[] # uncomment it to clear all devices
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
        self.period=int(Parameters["Mode4"])
        Domoticz.Heartbeat(self.period)
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        dev_exists={}
        for (unit,name,type,mul,formt) in self.devices:
            Domoticz.Debug("creating device %d %s" % (unit, name))
#            Domoticz.Device(fullname, Unit=unit+1, TypeName="Custom", Used=1).Create()
            type=type.split(':')[0]
            Domoticz.Device(name, Unit=unit+1, TypeName=type, Used=1).Create()
            dev_exists[unit]=True
        for unit in range(0,300):
            if unit in dev_exists: continue
            if unit+1 in Devices: Devices[unit+1].Delete()


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
                jednotka="" if ":" not in type else type.split(":")[1]
                Devices[unit+1].Update(0,format % val, Options={'Custom': '1;'+jednotka} )
#                Devices[unit+1].Update(0,format % val )
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
