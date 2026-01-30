from enum import Enum
from typing import List, Optional

# future, unused
class VType(Enum):
    OU1 = 1
    FB0 = 2
    FBC = 3
    OU  = 4
    AIN = 5

class Type(Enum):
    YY = 1 # OnOff, Analog Valve
    YF = 2 # Volumenstrom
    YT = 3 # Temperatur
    YL = 4 # Level
    YP = 5 # Pressure / (Tank)
    YN = 6 # VFD / Motor
    YB = 7 # Tank or Vessel
    YX = 8 # special Equipment
    YR = 9 # Radiation
    YG = 10 # Gaging/Switch
    YU = 11
    YZ = 12
    YQ = 13
    YS = 14
    UNKNOWN = 15


class Component:
    name: str
    ctype: Type
    # for future use
    read: Optional[VType]  
    write: Optional[VType] 
    connection_in: List["Component"] 
    connection_out: List["Component"] 

    def __init__(self,
                 name: str,
                 ctype: Type,
                 read: Optional[VType] = None,
                 write: Optional[VType] = None,
                 connection_in: Optional[List["Component"]] = None,
                 connection_out: Optional[List["Component"]] = None):
        self.name = name
        self.ctype = ctype
        self.read = read
        self.write = write
        self.connection_in = list(connection_in) if connection_in is not None else []
        self.connection_out = list(connection_out) if connection_out is not None else []

    def __repr__(self) -> str:
        ins  = [c.name for c in self.connection_in]
        outs = [c.name for c in self.connection_out]
        return (f"Component(name={self.name!r}, ctype={self.ctype!r}, "
                f"connection_in={ins!r}, connection_out={outs!r})")

    # future use
    def set_connection_in(self, component: "Component"):
        self.connection_in.append(component)

    def set_connection_out(self, component: "Component"):
        self.connection_out.append(component)

    #def print():

                  
