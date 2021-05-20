#Used packages and files
import Parameters

class Central_Bank(object):
    
    def __init__(self, bonds, cash_advances):
        self.bonds = bonds
        self.cash_advances = cash_advances

    def get_attribute(self, attribute):
        """
        Possible attributes:
            - 'bonds'
            - 'cash_advances'
        """
        if attribute == 'bonds':
            return self.bonds
        elif attribute == 'cash_advances':
            return self.cash_advances
        else:
            assert False
