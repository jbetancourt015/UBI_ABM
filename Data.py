import Households
import CFirms
import KFirms
import Banks
import Government
import CentralBank

class Data(object):

    def __init__(self):
        pass
    
    def create_household_dict(self, households, attributes):
        self.household_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        for household in households:
            dictionary = {}
            for attribute in attributes:
                assert type(attribute) == str
                dictionary[attribute] = []
            self.household_data[str(household.id)] = dictionary
    
    def create_Cfirm_dict(self, Cfirms, attributes):
        self.Cfirm_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        for firm in Cfirms:
            dictionary = {}
            for attribute in attributes:
                assert type(attribute) == str
                dictionary[attribute] = []
            self.Cfirm_data[str(firm.id)] = dictionary
    
    def create_Kfirm_dict(self, Kfirms, attributes):
        self.Kfirm_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        for firm in Kfirms:
            dictionary = {}
            for attribute in attributes:
                assert type(attribute) == str
                dictionary[attribute] = []
            self.Kfirm_data[str(firm.id)] = dictionary
    
    def create_bank_dict(self, banks, attributes):
        self.bank_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        for bank in banks:
            dictionary = {}
            for attribute in attributes:
                assert type(attribute) == str
                dictionary[attribute] = []
            self.bank_data[str(bank.id)] = dictionary

    def create_gov_dict(self, gov, attributes):
        self.gov_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        dictionary = {}
        for attribute in attributes:
            assert type(attribute) == str
            dictionary[attribute] = []
        self.gov_data = dictionary
    
    def create_centralbank_dict(self, gov, attributes):
        self.cb_data = {}
        if type(attributes) == str:
            attributes = [attributes]
        assert type(attributes) == list
        dictionary = {}
        for attribute in attributes:
            assert type(attribute) == str
            dictionary[attribute] = []
        self.cb_data = dictionary
    
    def update_data(self, list_or_agent, attributes):
        if type(attributes) == str:
            attributes = [attributes]
        assert (type(attributes) == list or type(attributes) == tuple)
        if type(list_or_agent) != list:
            list_or_agent == [list_or_agent]
        for agent in list_or_agent:
            if type(agent) == Households.Household:
                for attribute in attributes:
                    assert type(self.household_data[str(agent.id)][attribute]) == list
                    self.household_data[str(agent.id)][attribute].append(agent.get_attribute(attribute))
            elif type(agent) == KFirms.KFirm:
                assert type(self.kfirm_data[str(agent.id)][attribute]) == list
                self.kfirm_data[str(agent.id)][attribute].append(agent.get_attribute(attribute))
            elif type(agent) == CFirms.CFirm:
                assert type(self.cfirm_data[str(agent.id)][attribute]) == list
                self.cfirm_data[str(agent.id)][attribute].append(agent.get_attribute(attribute))
            elif type(agent) == Banks.Bank:
                assert type(self.bank_data[str(agent.id)][attribute]) == list
                self.bank_data[str(agent.id)][attribute].append(agent.get_attribute(attribute))
            elif type(agent) == Government.Gov:
                assert type(self.gov_data[attribute]) == list
                self.gov_data[attribute].append(agent.get_attribute(attribute))
            elif type(agent) == CentralBank.Central_Bank:
                assert type(self.cb_data[attribute]) == list
                self.cb_data[attribute].append(agent.get_attribute(attribute))
            else:
                assert False


        