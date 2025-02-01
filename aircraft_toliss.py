from Aircraft import Aircraft, DREF, DREF_TYPE

class Toliss_A319(Aircraft):
    def set_name(self, name):
        self.name = name

    def create_aircraft(self):
        #name = "test"
        print("Test")
        self.drefs = []
        self.drefs.append(DREF("AP1", "AirbusFBW/AP1Engage", DREF_TYPE.DATA))
        self.drefs.append(DREF("AP2", "AirbusFBW/AP2Engage", DREF_TYPE.DATA))
        self.drefs.append(DREF("R_RANGE 10", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA))
        self.drefs.append(DREF("R_RANGE 20", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA))
        self.drefs.append(DREF("R_RANGE 40", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA))
        #print(f"create aircraft {name}")


acf = Toliss_A319()
acf.set_name("Toliss A319 and compatibla")

acf.create_aircraft()
