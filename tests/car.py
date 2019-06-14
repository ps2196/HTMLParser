""""Class for testing serialization/ deserialization"""

class Engine:
    def __init__(self):
        self.power = None
        self.volume = None
        self.type = None

    def __str__(self):
        return 'Engine: \n\tPower:  '+str(self.power)+'\n\tVolume: '+str(self.volume)+"\n\tType: "+str(self.type)

class Car:
    def __init__(self):
        self.brand = None
        self.model_name = None
        self.engine = None
        self.vmax = None

    def __str__(self):
        return 'Car: \n\tBrand:  '+str(self.brand)+'\n\tModel: '+str(self.model_name)+'\n\tVmax: '+str(self.vmax)+"\n\t"+str(self.engine)

    def new_car():
        c = Car()
        c.vmax=200
        return c