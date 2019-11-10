"""
Systemair_SAVE_VTR is python wrapper for modbus communication with Systemair SAVE VTR units.
"""
REGMAP_INPUT = {
    'REG_FILTER_REMAINING_TIME_L':      {'addr':   7004, 'value': 0},#Remaining filter time in seconds, lower 16 bits
    'REG_SENSOR_SAT':                   {'addr':  12102, 'value': 0},#Supply Air Temperature sensor (standard)
    'REG_SENSOR_OAT':                   {'addr':  12101, 'value': 0},#Outdoor Air Temperature sensor (standard)
    'REG_OUTPUT_Y3_DIGITAL':            {'addr':  14201, 'value': 0},#Cooler DO state:0: Output not active1: Output active
    'REG_OUTPUT_Y3_ANALOG':             {'addr':  14200, 'value': 0},#Cooler AO state
    'REG_OUTPUT_Y2_DIGITAL':            {'addr':  14103, 'value': 0},#Heat Exchanger DO state.0: Output not active1: Output active
    'REG_OUTPUT_Y2_ANALOG':             {'addr':  14102, 'value': 0},#Heat Exchanger AO state.
    'REG_OUTPUT_Y1_DIGITAL':            {'addr':  14101, 'value': 0},#Heater DO state:0: Output not active1: Output active
    'REG_OUTPUT_Y1_ANALOG':             {'addr':  14100, 'value': 0},#Heater AO state.
    'REG_FILTER_ALARM_WAS_DETECTED':    {'addr':   7006, 'value': 0},#Indicates if the filter warning alarm was generated.
    'REG_TC_SP_SATC':                   {'addr':   2053, 'value': 0},#Temperature setpoint for the supply air temperature
    'REG_USERMODE_MODE':                {'addr':   1160, 'value': 0},#Active User mode.0: Auto1: Manual2: Crowded3: Refresh4: Fireplace5: Away6: Holiday7: Cooker Hood8: Vacuum Cleaner9: CDI110: CDI211: CDI312: PressureGuard
    'REG_SENSOR_PDM_EAT_VALUE':         {'addr':  12543, 'value': 0}#PDM EAT sensor value (standard)
}
REGMAP_HOLDING = {
    'REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF':    {'addr':  1130, 'value': 0}, #Fan speed level for mode Manual, supply fan.(1): value Off only allowed if contents of register 1352 is 1.(1): Off 2: Low 3: Normal 4:High
    'REG_USERMODE_MANUAL_AIRFLOW_LEVEL_EAF':    {'addr':  1131, 'value': 0}, #Fan speed level for mode Manual, extract fan. 2: Low 3: Normal 4: High
    'REG_TC_SP':                                {'addr':  2000, 'value': 0} #Temperature setpoint for the supply air temperature
}


class SystemairSaveVTR(object):
    """
    Class SystemairSaveVTR used to represent a Systemair SAVE VTR unit.

    Attributes
    ----------
    _input_regs : dict
        A dictionary with input registers.
    _holding_regs : dict
        A dictionary with holding registers.
    _slave : int
        Slave number of the unit.
    _conn : ModbusClient
        Modbus client used to communicate with the unit.
    """
    def __init__(self, conn, slave, update_on_read=False):
        self._conn = conn
        self._input_regs = REGMAP_INPUT
        self._holding_regs = REGMAP_HOLDING
        self._slave = slave
        self._setpoint_temp = None
        self._supply_temp = None
        self._extract_temp = None
        self._outdoor_temp = None
        self._user_mode = None
        self._heater = None
        self._heater_state = None
        self._filter_warning = None
        self._filter_remaining_hours = None
        self._heat_exchanger = None
        self._heat_exchanger_state = None
        self._cooler = None
        self._cooler_state = None
        self._fan_speed_supply = None
        self._fan_speed_extract = None
        self._update_on_read = update_on_read

    def update(self):
        """
        Updates all of the input and holding regs dict values.
        """
        ret = True
        try:
            for k in self._input_regs:
                self._input_regs[k]['value'] = \
                    self._conn.read_holding_registers(
                        unit=self._slave,
                        address=self._input_regs[k]['addr']
                    ).registers
            for k in self._holding_regs:
                self._holding_regs[k]['value'] = \
                    self._conn.read_holding_registers(
                        unit=self._slave,
                        address=self._holding_regs[k]['addr']
                    ).registers
        except AttributeError:
            # The unit does not reply reliably
            ret = False
            print("Modbus read failed")

        self._setpoint_temp = \
            (self._input_regs['REG_TC_SP_SATC']['value'][0] / 10.0)
        self._supply_temp = \
            (self._input_regs['REG_SENSOR_SAT']['value'][0] / 10.0)
        self._extract_temp = \
            (self._input_regs['REG_SENSOR_PDM_EAT_VALUE']['value'][0] / 10.0)
        self._outdoor_temp = \
            (self.get_twos_comp(self._input_regs['REG_SENSOR_OAT']['value'][0]) / 10.0)
        self._user_mode = \
            self.get_user_mode_switch(self._input_regs['REG_USERMODE_MODE']['value'][0])
        self._filter_warning = \
            bool(self._input_regs['REG_FILTER_ALARM_WAS_DETECTED']['value'][0])
        self._filter_remaining_hours = \
            (self._input_regs['REG_FILTER_REMAINING_TIME_L']['value'][0] / 60 / 60)
        self._heater = \
            bool(self._input_regs['REG_OUTPUT_Y1_DIGITAL']['value'][0])
        self._heater_state = \
            (self._input_regs['REG_OUTPUT_Y1_ANALOG']['value'][0])
        self._heat_exchanger = \
            bool(self._input_regs['REG_OUTPUT_Y2_DIGITAL']['value'][0])
        self._heat_exchanger_state = \
            (self._input_regs['REG_OUTPUT_Y2_ANALOG']['value'][0])
        self._cooler = \
            bool(self._input_regs['REG_OUTPUT_Y3_DIGITAL']['value'][0])
        self._cooler_state = \
            (self._input_regs['REG_OUTPUT_Y3_ANALOG']['value'][0])
        self._fan_speed_supply = \
            (self._holding_regs['REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF']['value'][0])
        self._fan_speed_extract = \
            (self._holding_regs['REG_USERMODE_MANUAL_AIRFLOW_LEVEL_EAF']['value'][0])

        return ret

    @staticmethod
    def get_twos_comp(argument):
        if argument > 32767:
            return -(65535 - argument)
        else:
            return argument

    @staticmethod
    def get_user_mode_switch(argument):
        switcher = {
            0: "Auto",
            1: "Manual",
            2: "Crowded",
            3: "Refresh",
            4: "Fireplace",
            5: "Away",
            6: "Holiday",
            7: "Cooker Hood",
            8: "Vacuum Cleaner",
            9: "CDI1",
            11: "CDI2",
            12: "PressureGuard",
        }
        return switcher.get(argument, "nothing")

    def get_raw_input_register(self, name):
        """Get raw register value by name."""
        if self._update_on_read:
            self.update()
        return self._input_regs[name]

    def get_raw_holding_register(self, name):
        """Get raw register value by name."""
        if self._update_on_read:
            self.update()
        return self._holding_regs[name]

    def set_raw_holding_register(self, name, value):
        """Write to register by name."""
        self._conn.write_register(
            unit=self._slave,
            address=(self._holding_regs[name]['addr']),
            value=value)

    def set_fan_speed_supply(self, fan):
        """Set fan speed supply."""
        self._conn.write_register(
            unit=self._slave,
            address=(self._holding_regs['REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF']['addr']),
            value=fan)

    @property
    def get_fan_speed_supply(self):
        """Get fan speed supply."""
        if self._update_on_read:
            self.update()
        return self._fan_speed_supply

    def set_fan_speed_extract(self, fan):
        """Set fan speed extract."""
        self._conn.write_register(
            unit=self._slave,
            address=(self._holding_regs['REG_USERMODE_MANUAL_AIRFLOW_LEVEL_EAF']['addr']),
            value=fan)

    @property
    def get_fan_speed_extract(self):
        """Get fan speed extract."""
        if self._update_on_read:
            self.update()
        return self._fan_speed_extract

    @property
    def get_supply_temp(self):
        """Get supply temperature."""
        if self._update_on_read:
            self.update()
        return self._supply_temp

    def set_setpoint_temp(self, temp):
        self._conn.write_register(
            unit=self._slave,
            address=(self._holding_regs['REG_TC_SP']['addr']),
            value=round(temp * 10.0))

    @property
    def get_setpoint_temp(self):
        """Get setpoint temperature."""
        if self._update_on_read:
            self.update()
        return self._setpoint_temp

    @property
    def get_user_mode(self):
        """Get the set user mode."""
        if self._update_on_read:
            self.update()
        return self._user_mode

    @property
    def get_extract_temp(self):
        """Get the extract temperature."""
        if self._update_on_read:
            self.update()
        return self._extract_temp

    @property
    def get_outdoor_temp(self):
        """Get the extract temperature."""
        if self._update_on_read:
            self.update()
        return self._outdoor_temp

    @property
    def get_filter_warning(self):
        """If filter warning has been generated."""
        if self._update_on_read:
            self.update()
        return self._filter_warning

    @property
    def get_filter_remaining_hours(self):
        """Return remaining filter hours."""
        if self._update_on_read:
            self.update()
        return self._filter_remaining_hours

    @property
    def get_heater(self):
        """Is heater active."""
        if self._update_on_read:
            self.update()
        return self._heater

    @property
    def get_heater_state(self):
        """Return heater state."""
        if self._update_on_read:
            self.update()
        return self._heater_state

    @property
    def get_heat_exchanger(self):
        """Is heat exchanger active."""
        if self._update_on_read:
            self.update()
        return self._heat_exchanger

    @property
    def get_heat_exchanger_state(self):
        """Return heat exchanger state."""
        if self._update_on_read:
            self.update()
        return self._heat_exchanger_state

    @property
    def get_cooler(self):
        """Is cooler active."""
        if self._update_on_read:
            self.update()
        return self._cooler

    @property
    def get_cooler_state(self):
        """Return cooler state."""
        if self._update_on_read:
            self.update()
        return self._cooler_state
