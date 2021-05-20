#Used packages and files
import Parameters
import Transaction

class Gov(object):
    
    def __init__(self, bonds, reserves, bond_payment=None, 
                 cash_advances_payment=None, tax_payment=None, 
                 wage_payment=None, dole_payment=None, employees=None):
        self.bonds = bonds
        self.reserves = reserves
        self.bond_payment = bond_payment
        self.cash_advances_payment = cash_advances_payment
        self.tax_payment = tax_payment
        self.wage_payment = wage_payment
        self.dole_payment = dole_payment
        self.employees = []

    def get_attribute(self, attribute):
        """
        Possible attributes:
            - 'bonds'
            - 'reserves'
            - 'bond_payment'
            - 'cash_advances_payment'
            - 'tax_payment'
            - 'wage_payment'
            - 'dole_payment'
            - 'employees'
        """
        if attribute == 'bonds':
            return self.bonds
        elif attribute == 'reserves':
            return self.reserves
        elif attribute == 'bond_payment':
            return self.bond_payment
        elif attribute == 'cash_advances_payment':
            return self.cash_advances_payment
        elif attribute == 'tax_payment':
            return self.tax_payment
        elif attribute == 'wage_payment':
            return self.wage_payment
        elif attribute == 'dole_payment':
            return self.dole_payment
        elif attribute == 'employees':
            return self.employees
        else:
            assert False
        
    
    #Payments are reset
    def reset_payments(self):
        self.tax_payment = 0
        self.wage_payment = 0
        self.bond_payment = 0
        self.cash_advances_payment = 0
        self.dole_payment = 0

    #Wage payment
    def pay_wages(self):
        for household in self.employees:
            amount = Transaction.transaction(amount = household.res_wage, payer = self, receiver = household, output = True)
            household.income += amount
            self.wage_payment += amount

    #Dole payment
    def pay_dole(self, household, avg_wage):
        dole = Parameters.Dole_proportion*avg_wage
        amount = Transaction.transaction(amount = dole, payer = self, receiver = household, output = True)
        household.income += amount
        self.dole_payment += amount

    #Bond emission
    def emit_bonds(self):
        self.bonds = max(0, (self.wage_payment + self.dole_payment + self.bond_payment 
                             - self.tax_payment + self.cash_advances_payment)/Parameters.Bonds_price)
    