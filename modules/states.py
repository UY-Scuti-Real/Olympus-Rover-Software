# command & control states


class state:
    state_dict = {}

    def __init__(self):
        pass

    def __eq__(self, compared_to):
        if issubclass(compared_to, state):
            is_equal = True
            for code, value in self.state_dict.items():
                if code in compared_to.state_dict:
                    if value != compared_to.state_dict[code]:
                        is_equal = False
            return is_equal

    def __repr__(self):
        code_str = value_str = ""
        for code, value in self.state_dict.items():
            code_str += str(code) + '\t'
            value_str += str(value) + '\t'
        return code_str + '\n' + value_str + '\n' 
