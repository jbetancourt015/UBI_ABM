#Used packages and files
import Parameters
import numpy as np
import Transaction

#Expectations function
def expectation(actual, exp=None):
    phi = Parameters.Adaptative_expectations
    if exp==None:
        exp = actual
    return phi*exp + (1-phi)*actual

class Household(object):
    
    def __init__(self, identification, deposits, interest_on_deposits, res_wage, 
                 last_price, net_disposable_income, desired_consumption, 
                 employer=None, old_supplier=None, deposits_bank=None, 
                 exp_price=None, unem_hist=None, periods_unem=None, 
                 supplier=None, income=None, wealth_pre=None, tax=None):
        
        self.id = 'HH_' + str(identification)
        self.deposits = deposits
        self.interest_on_deposits = interest_on_deposits
        self.res_wage = res_wage
        self.last_price = last_price
        self.net_disposable_income = net_disposable_income
        self.desired_consumption = desired_consumption
        self.employer = employer
        self.old_supplier = old_supplier
        self.deposits_bank = deposits_bank
        self.exp_price = exp_price
        self.unem_hist = unem_hist
        self.periods_unem = periods_unem
        self.supplier = supplier
        self.income = income
        self.wealth_pre = wealth_pre
        self.tax = tax
    
    def get_attribute(self, attribute):
        """
        Possible attributes:
            - 'id'
            - 'deposits'
            - 'interest_on_deposits'
            - 'res_wage'
            - 'last_price'
            - 'net_disposable_income'
            - 'desired_consumption'
            - 'employer'
            - 'old_supplier'
            - 'deposits_bank'
            - 'exp_price'
            - 'unem_hist'
            - 'periods_unem'
            - 'supplier'
            - 'income'
            - 'wealth_pre'
            - 'tax'
        """
        if attribute == 'id':
            return self.id
        elif attribute == 'deposits':
            return self.deposits
        elif attribute == 'interest_on_deposits':
            return self.interest_on_deposits
        elif attribute == 'res_wage':
            return self.res_wage
        elif attribute == 'last_price':
            return self.last_price
        elif attribute == 'net_disposable_income':
            return self.net_disposable_income
        elif attribute == 'desired_consumption':
            return self.desired_consumption
        elif attribute == 'employer':
            if self.employer != None:
                return self.employer.id
            else:
                return self.employer
        elif attribute == 'old_supplier':
            if self.old_supplier != None:
                return self.old_supplier.id
            else:
                return self.old_supplier
        elif attribute == 'deposits_bank':
            if self.deposits_bank != None:
                return self.deposits_bank.id
            else:
                return self.deposits_bank
        elif attribute == 'exp_price':
            return self.exp_price
        elif attribute == 'unem_hist':
            return self.unem_hist
        elif attribute == 'periods_unem':
            return self.periods_unem
        elif attribute == 'supplier':
            if self.supplier != None:
                return self.supplier.id
            else:
                return self.supplier
        elif attribute == 'income':
            return self.income
        elif attribute == 'wealth_pre':
            return self.wealth_pre
        elif attribute == 'tax':
            return self.tax
        else:
            assert False
        
    #Plan consumption
    def plan_consumption(self):
        alpha_1 = Parameters.Propensity_to_consume_income
        alpha_2 = Parameters.Propensity_to_consume_wealth
        
        self.exp_price = expectation(self.last_price, self.exp_price)
        self.desired_consumption = (1/self.exp_price)*(alpha_1*self.net_disposable_income 
                                                       + alpha_2*self.deposits)
        assert self.desired_consumption >= - Parameters.Precision
        self.desired_consumption = max(0, self.desired_consumption)
    
    #Update the reservation wage
    def update_res_wage(self, u_rate):
        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        change = 1
        
        if self.employer == None and self.periods_unem > 2:
            change = 1 - abs(np.random.normal(FNmean,FNsd))
            while change <= 0:
                change = 1 - abs(np.random.normal(FNmean,FNsd))
        if self.employer!=None and self.periods_unem<=2 and u_rate<=Parameters.Initial_unemployment:
            change = 1 + abs(np.random.normal(FNmean,FNsd))
        self.res_wage = self.res_wage*change
        assert self.res_wage > 0
    
    #Tax payment
    def pay_taxes(self, gov):
        amount = min(self.deposits, self.tax)
        amount = Transaction.transaction(amount, payer = self, receiver = gov, output = True)
        gov.tax_payment += amount
        
        self.net_disposable_income = self.income - amount
        assert self.deposits >= - Parameters.Precision
        self.deposits = max(0, self.deposits)