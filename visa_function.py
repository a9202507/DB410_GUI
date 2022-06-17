import pyvisa
import time
import pathlib
from datetime import datetime
rm = pyvisa.ResourceManager()


def get_visa_resource_list(remove_ASRL_devices=False):
    rm = pyvisa.ResourceManager()
    device_list = rm.list_resources()

    if remove_ASRL_devices == True:
        filtered = filter(lambda device: "ASRL" not in device, device_list)
        device_list = list(filtered)
    else:
        pass

    return device_list


def create_visa_equipment(resource_name):
    equipment = rm.open_resource(resource_name)

    return equipment


class visa_equipment():
    def __init__(self, visa_resource_name):
        self.visa_resource_name = visa_resource_name
        self.inst = pyvisa.ResourceManager().open_resource(self.visa_resource_name)
    '''
    def write(self, visa_str=""):
        self.inst.write(visa_str)

    def query(self, visa_str=""):
        self.inst.query(visa_str)
    '''

    def get_equipment_name(self):
        self.equipment_name = self.inst.query("*IDN?")
        return self.equipment_name


class tek_visa_equipment(visa_equipment):
    def __init__(self, visa_resource_name):
        visa_equipment.__init__(self, visa_resource_name)

    def on(self):
        self.inst.write("OUTPut1:STATe ON")

    def off(self):
        self.inst.write("OUTPut1:STATe off")


class tek_visa_functionGen(tek_visa_equipment):
    def __init__(self, visa_resource_name, shape="PULS"):
        tek_visa_equipment.__init__(self, visa_resource_name)
        self.set_waveform_shape(shape)

    def set_freq(self, freq_khz):
        self.inst.write("SOURce1:FREQuency:FIXed "+str(freq_khz)+"kHz")

    def set_duty(self, duty):
        self.inst.write("SOURce1:PULSe:DCYCLe "+str(duty))

    def set_rise_time_ns(self, rise_time):
        self.inst.write("SOURce1:PULSe:TRANsition:LEADing " +
                        str(rise_time)+"ns")

    def set_fall_time_ns(self, fall_time):
        self.inst.write("SOURce1:PULSe:TRANsition:TRAiling " +
                        str(fall_time)+"ns")

    def set_waveform_shape(self, shape="PULS"):
        self.inst.write("SOURce1:FUNCtion:SHAPe "+shape)

    def set_voltage_high(self, voltage=0):
        self.inst.write("SOURce1:VOLTage:LEVel:IMMediate:High "+str(voltage))

    def set_voltage_low(self, voltage=0):
        self.inst.write("SOURce1:VOLTage:LEVel:IMMediate:Low "+str(voltage))

    def get_rise_time_ns(self):
        return self.inst.query("SOURce1:PULSe:TRANsition:LEADing?")


class tek_visa_mso_escope(visa_equipment):
    def __init__(self, visa_resource_name):
        visa_equipment.__init__(self, visa_resource_name)

    def save_waveform_in_inst(self, file_save_location_in_inst, filename, timestamp_enable=True, debug=False):
        self.file_save_path = pathlib.Path(file_save_location_in_inst)
        dt = datetime.now()
        if timestamp_enable == True:
            timestamp = dt.strftime("_%Y%m%d_%H%M%S")
            self.filename_in_inst = filename+timestamp
        else:
            self.filename_in_inst = filename
        self.filename_in_inst += ".png"
        self.filename_with_path_in_inst = "'" + \
            str(self.file_save_path / self.filename_in_inst) + "'"
        self.inst.write(('SAVE:IMAGe '+self.filename_with_path_in_inst))

        if debug == True:
            print(('SAVE:IMAGe '+self.filename_with_path_in_inst))

    def read_file_in_inst(self, inst_directory, filename):
        inst_direct_filename = inst_directory+"/"+filename
        self.inst.write(f"FileSystem:READFile '{inst_direct_filename}'")

    # TODO:
    def save_waveform_back_to_pc(self, inst_directory, filename, local_directory="./report/", debug=False):

        inst_direct_filename = inst_directory+"/"+filename
        if debug == True:
            print(f'save wavfrom:{inst_direct_filename}')
        self.inst.write(f"FileSystem:READFile '{inst_direct_filename}'")
        imgData = self.inst.read_raw(1024*1024)
        pc_dicrect_filename = local_directory+filename
        file = open(pc_dicrect_filename, "wb")
        file.write(imgData)
        file.close()
        return None

    def set_waveform_directory_in_scope(self, directory="E:/20220530"):
        self.inst.write(f"FILESystem:CWD '{directory}'")

    def get_waveform_directory_in_scope(self):
        directory = self.inst.query(f"FILESystem:CWD?")
        return directory

    def set_channel_measure_items(self):
        pass

    def get_measurement_value(self, item_number="1", measure_item_type="max"):
        measure_type_dict = {"max": "MAXIMUM",
                             "min": "MINIMUM",
                             "mean": "MEAN",
                             "value": "value", }
        result = self.inst.query(
            "MEASUrement:MEAS"+str(item_number)+":RESUlts:CURRentacq:"+measure_type_dict[measure_item_type]+"?")
        return result

    def set_horizontal_scale(self, scale="2e-6"):
        self.inst.write("HORIZONTAL:SCAlE "+scale)

    def set_trigger_level(self, trigger_level="1.0"):
        self.inst.write("TRIGger:A:level "+trigger_level)

    def set_trigger_channel(self, channel="CH1"):
        self.inst.write(f"TRIGger:A:EDGE:SOURCE {channel}")


def save_waveform_in_inst(visaRsrcAddr, fileSaveLocationInInst, filename, timestamp_enable=True, debug=False):
    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(visaRsrcAddr)
    visaRsrcAddr = visaRsrcAddr
    fileSaveLocation2 = pathlib.Path(fileSaveLocationInInst)
    dt = datetime.now()
    timestamp = dt.strftime("MSO56_%Y%m%d_%H%M%S.png")
    if timestamp_enable == True:
        filename_in_inst = filename+timestamp
    else:
        filename_in_inst = filename

    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(visaRsrcAddr)

    path_filename_in_inst = "'"+str(fileSaveLocation2 / filename_in_inst)+"'"
    scope.write('SAVE:IMAGe '+path_filename_in_inst)
    if debug == True:

        print(scope.query('*IDN?'))  # Print instrument id to console window

        print('SAVE:IMAGe '+path_filename_in_inst)
    scope.close()
    rm.close()


if __name__ == '__main__':

    devices = get_visa_resource_list()
    print(devices)
    # escope=create_visa_equipment(devices[0])
    # print(escope.query('*IDN?'))
    #fungen = tek_visa_functionGen(devices[4])
    scope = tek_visa_mso_escope(devices[0])

    for i in range(1,20):
        value=scope.get_measurement_value(1,"mean")
        print(value)

    
    
    '''
    scope.save_waveform_in_inst("E:/20220530", "12345", False, True)
    scope.save_waveform_back_to_pc(
        "E:/20220530", "12345.png", "./report/", True)

    
    freqs = [10, 20, 100, 200]
    dutys = [10, 20, 50]

    # work with DPO4104
    for freq in freqs:
        for duty in dutys:

            fungen.set_duty(duty)
            fungen.set_freq(freq)
            fungen.on()
            time.sleep(2)
            scope.save_waveform_in_inst(
                "C:/Users/Tek_Local_Admin/Desktop/Eason", f"Eason_mso56_{freq}khz_D{duty}", True, True)
            time.sleep(5)
            fungen.off()
            time.sleep(2)
            

    
>>> scope.inst.query("MEASUrement:MEAS1:MAXIMUM?")
'550.0000E-3\n'
>>> scope.inst.query("MEASUrement:MEAS1:MEAN?")

'''
