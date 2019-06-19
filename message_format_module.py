#  message format module
default_format = {"header": str, "value": float, "delimiter": ':'}
default_filter = filter(default_format)


class filter:
    """
    init expects:
        dict cmd_format,
        [dict valid_cmds]
    call expects:
        dict cmd or str cmd
    Usage:
        Initiate in code or at run-time. When passed to validate_cmds, is
        applied to all commands.
        on call validates the passed commands. can be raw strings cmd or dict
        cmd (post-decoding). if command passes the filter, it is returned.

        cmd_format is a dictionary with supported keys:
            "header", "value", "range", "delimiter", "conditional"
        "header" and "value" must be the expected type, for example:
            {"header":str, "value":float"}
        Minimum acceptable cmd_format contains header and value.
        if "range" is not none, "value" is assumed to be a float between
        range[0] and range[1]
        if "function" is not none, the function will be applied to the value
        field. if True/False returns, will just pass value if True

    """

    def __init__(self, cmd_fmt, valid_cmds=False):
        self.cmd_fmt = cmd_fmt
        self.valid_cmds = valid_cmds

    def __call__(self, cmds):
        valid_cmds = {}
        for i in range(len(cmds)):
            cmd_tuple = cmds.popitem()
            checked_cmd = self._validate_cmd(*cmd_tuple)
            if checked_cmd is not None:
                valid_cmds[checked_cmd[0]] = checked_cmd[1]
        return valid_cmds

    def _validate_cmd(self, cmd, value):
        valid = True
        try:
            cmd = self.cmd_fmt["header"](cmd)
            value = self.cmd_fmt["value"](value)
        except ValueError:
            # if you can't float the value, it shouldn't pass
            valid = False
            return 0

        if "range" in self.cmd_fmt:
            if self.cmd_fmt["range"][0] < value < self.cmd_fmt["range"][1]:
                pass
            else:
                valid = False

        if "function" in self.cmd_fmt:
            value_check = self.cmd_fmt["function"](value)
            if value_check is not True and value_check is not False:
                value = value_check
            elif not value_check:
                valid = False

        if self.valid_cmds:
            if cmd in self.valid_cmds:
                pass
            else:
                valid = False

        if valid:
            return cmd, value
        else:
            return None


def validate_cmds(cmd_dict, filter_obj=default_filter):
    return filter_obj(cmd_dict)


def get_dictcmds_from_str(string_message):
    cmd_dict = {}
    if ',' in string_message:
        cmd_list = string_message.split(':')
    for cmd in cmd_list:
        if len(cmd) > 0 and ':' in cmd:
            cmd_name, cmd_value = cmd.split(':')
            cmd_dict[cmd_name] = cmd_value
    return cmd_dict


def get_strcmds_from_dict(cmd_dict, cmd_format=default_format):
    string = ""
    for key, value in cmd_dict.items():
        string += key + default_format["delimiter"] + str(value) + ','
    return string
