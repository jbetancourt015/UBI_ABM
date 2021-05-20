#Used packages and files
import Parameters
import numpy as np
import math
import Transaction
import random

#Expectations function
def expectation(actual, exp=None):
    phi = Parameters.Adaptative_expectations
    if exp==None:
        exp = actual
    out = phi*exp + (1-phi)*actual
    assert out >= - Parameters.Precision
    out = max(0, out)
    return out

class CFirm(object):
    
    def __init__(self, identification, mark_up, deposits, interest_on_deposits, sales,
                 inventories, inventories_past, output, price, unit_cost_present,
                 OCF, profit_rate, profit_post_tax, K_sheet, K_stock,
                 loan_granted, loan_sheet, type='C', supplier_list=None, status=None,
                 old_supplier=None, old_bank=None, deposits_bank=None, 
                 exp_sales=None, exp_OCF=None, exp_profit_post_tax=None, 
                 exp_avg_wage=None, desired_output=None,
                 desired_capacity_utilization=None, desired_n_employees=None,
                 planned_output=None, avg_wage=None, K_demand=None,
                 obsolete_K=None, loan_requirement=None, extra_L_needed=None,
                 past_K_value=None, revenue=None, tax=None):
        
        self.id = 'CF_' + str(identification)
        self.mark_up = mark_up
        self.deposits = deposits
        self.interest_on_deposits = interest_on_deposits
        self.sales = sales
        self.inventories = inventories
        self.inventories_past = inventories_past
        self.output = output
        self.price = price
        self.unit_cost_present = unit_cost_present
        self.OCF = OCF
        self.cashFlowRate = profit_rate
        self.profit_post_tax = profit_post_tax
        self.K_sheet = K_sheet
        self.K_stock = K_stock
        self.loan_granted = loan_granted
        self.loan_sheet = loan_sheet
        self.type = type
        self.supplier_list = supplier_list
        self.status = status
        self.old_supplier = old_supplier
        self.old_bank = old_bank 
        self.deposits_bank = deposits_bank 
        self.exp_sales = exp_sales 
        self.exp_OCF = exp_OCF 
        self.exp_profit_post_tax = exp_profit_post_tax 
        self.exp_avg_wage = exp_avg_wage
        self.desired_output = desired_output
        self.desired_capacity_utilization = desired_capacity_utilization
        self.desired_n_employees = desired_n_employees
        self.planned_output = planned_output
        self.avg_wage = avg_wage
        self.K_demand = K_demand
        self.obsolete_K = obsolete_K
        self.loan_requirement = loan_requirement
        self.extra_L_needed = extra_L_needed
        self.past_K_value = past_K_value
        self.revenue = revenue
        self.tax = tax
        self.employees = []
        
    #Calculate stock of capital
    def calculate_K_stock(self):
        total_K_stock = 0
        for capital in self.K_sheet:
            total_K_stock += capital['Quantity']
        self.K_stock = total_K_stock
    
    #Capital age is updated and obsolete capital is calculated
    def age_K(self):
        obs_K = 0
        for capital in self.K_sheet:
            capital['Age'] += 1
            if capital['Age'] == Parameters.K_goods_duration:
                obs_K += capital['Quantity']
        assert obs_K >= 0
        self.obsolete_K = obs_K
        capitalList = self.K_sheet[:]
        for capital in capitalList:
            if capital['Age'] > Parameters.K_goods_duration:
                self.K_sheet.remove(capital)
        for capital in self.K_sheet:
            assert capital['Age'] <= Parameters.K_goods_duration
        
        # obs_K = 0
        # iterator = 0
        # while True:
        #     try:
        #         capital = self.K_sheet[iterator]
        #     except IndexError:
        #         break
        #     else:
        #         capital['Age'] += 1
        #         if capital['Age'] > Parameters.K_goods_duration:
        #             self.K_sheet.remove(capital)
        #         elif capital['Age'] == Parameters.K_goods_duration:
        #             obs_K += capital['Quantity']
        #             iterator += 1
        #         else:
        #             iterator += 1
        # self.obsolete_K = obs_K
    
    #Loan age is updated
    def age_Loan(self):
        for loan in self.loan_sheet:
            loan['Age'] += 1
        loanList = self.loan_sheet:
        for loan in loanList:
            if loan['Age'] > Parameters.Loans_duration:
                self.loan_sheet.remove(loan)
        for loan in self.loan_sheet:
            assert loan['Age'] <= Parameters.Loans_duration
    
    #Calculate aggregate wages
    def computeWageBill(self):
        agg_wages = 0
        for employee in self.employees:
            agg_wages += employee.res_wage
        assert agg_wages >= 0
        return agg_wages
    
    #Calculate amortization
    def computeAmortisation(self):
        amortization = 0
        for capital in self.K_sheet: #['Quantity':a, 'Age':b, 'Price':c, 'Value':d, 'Supplier':e]
            if capital['Age'] > 0:
                amortization += capital['Quantity']*capital['Price']/Parameters.K_goods_duration
        assert amortization >= 0
        return amortization

    #Output planning function for the current period
    def determineOutput(self):
        self.age_K() #Not in source code
        self.age_Loan() #Not in source code
        """
        Source: jmab\src\jmab\strategies\TargetExpectedInventoriesOutputStrategy
        """
        buffer = Parameters.Inventories_target_share
        expSales = self.exp_sales
        invQuantity = self.inventories
        expInv = self.exp_sales*buffer
        self.desiredOutput = max(0, expSales + (expInv - invQuantity))
        self.active['MKT_CAPGOOD'] = True #self.active is a dictionary for events

        #desiredOutput as constrained by capital?


    #Calculate the required amount of workers:
    def getRequiredWorkers(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        self.calculate_K_stock()
        totalProductivity = self.K_stock*Parameters.K_productivity
        residualOutput = self.desiredOutput
        if residualOutput > totalProductivity:
            requiredWorkers = self.K_stock/Parameters.K_L_ratio
        else:
            requiredCapital = residualOutput/Parameters.K_productivity
            requiredWorkers = requiredCapital/Parameters.K_L_ratio
        assert requiredWorkers >= 0
        self.requiredWorkers = round(requiredWorkers)

        #Inventories as share of sales
    def getReferenceVariableForPrice(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """

        inventories = self.inventories
        pastSales = self.sales
        return inventories/pastSales

        #What if pastSales = 0?
    
    #Price lower bound:
    def getPriceLowerBound(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        self.getRequiredWorkers() #Not in source code
        expectedAverageCosts = 0
        if self.desiredOutput > 0:
            expectedVariableCosts = self.exp_avg_wage*self.requiredWorkers
            expectedAverageCosts = expectedVariableCosts/self.desiredOutput
        else:
            totalProductivity = self.K_stock*Parameters.K_productivity
            residualOutput = self.inventories
            if residualOutput > totalProductivity:
                requiredWorkers = self.K_stock/Parameters.K_L_ratio
            else:
                requiredCapital = residualOutput/Parameters.K_productivity
                requiredWorkers = requiredCapital/Parameters.K_L_ratio
            assert requiredWorkers >= 0
            requiredWorkers = round(requiredWorkers)
            expectedVariableCosts = self.exp_avg_wage*requiredWorkers
            expectedAverageCosts = expectedVariableCosts/self.inventories
        assert expectedAverageCosts >= 0
        return expectedAverageCosts
        
        #What in the case of capital constrained production?
        #expectedVariableCosts vs expectedTotalCosts?

    #Set price
    def computePrice(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\AdaptiveMarkUpAveragePrice
        """

        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        threshold = Parameters.Inventories_target_share
        
        referenceVariable = self.getReferenceVariableForPrice()
        price = self.price
        markUp = self.mark_up
        previousLowerBound = price/(1 + markUp)

        if referenceVariable > threshold:
            mark_up_change = abs(np.random.normal(FNmean,FNsd))
            while mark_up_change >= 1:
                mark_up_change = abs(np.random.normal(FNmean,FNsd))
            markUp -= markUp*mark_up_change
        else:
            mark_up_change = abs(np.random.normal(FNmean,FNsd))
            markUp += markUp*mark_up_change
        assert markUp > 0
        self.mark_up = markUp

        priceLowerBound = self.getPriceLowerBound()

        if priceLowerBound != 0:
            price = priceLowerBound*(1 + markUp)
        else:
            price = previousLowerBound*(1 + markUp)
        
        if price > priceLowerBound:
            price = price
        else:
            price = priceLowerBound
        
        assert price > 0
        self.price = price

    #Compute Desired Capacity Growth
    def getDesiredCapacityGrowth(self):
        """
        Source: \benchmark-master\benchmark\src\benchmark\strategies\InvestmentCapacityOperatingCashFlowExpected
        """

        cashFlowRateWeight = Parameters.Profit_rate_weight
        capacityWeight = Parameters.Capacity_utilization_rate_weight
        targetCashFlow = Parameters.Target_profit_rate
        targetCapacityUtlization = Parameters.Target_capacity_utilizatio

        capitalStock = self.K_stock
        if capitalStock != 0:
            capacity = self.K_stock*Parameters.K_productivity
        
        desiredOutput = self.desiredOutput
        capitalValue = self.pastCapitalValue #Must calculate
        cashFlowRate = self.OCF/capitalValue
        self.cashFlowRate = cashFlowRate
        if capacity == 0 or capitalValue == 0:
            return -1
        else:
            desiredRateOfGrowth = (cashFlowRateWeight*(cashFlowRate - targetCashFlow)/targetCashFlow 
                                    + capacityWeight*((desiredOutput/capacity) - targetCapacityUtlization)/targetCapacityUtlization)
            return max(-1, desiredRateOfGrowth)

    #The demand for capital goods is calculated
    def computeRealCapitalDemand(self):
        """
        Source: jmab\src\jmab\strategies\RealCapitalDemandSimple
        """

        currentCapacity = self.K_stock*Parameters.K_productivity
        residualCapacity = (self.K_stock - self.obsolete_K)*Parameters.K_productivity
        desiredCapacity = (1 + self.getDesiredCapacityGrowth())*currentCapacity
        newCapitalRealDemand = int(math.ceil((desiredCapacity - residualCapacity)/Parameters.K_productivity))
        return newCapitalRealDemand

        #Possibility of negative demand?

    #Compute desired investment
    def computeDesiredInvestment(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """

        self.desiredRealCapitalDemand = self.computeRealCapitalDemand()
        if self.desiredRealCapitalDemand > 0:
            self.active['MKT_CAPGOOD'] = True
    
    #Compute debt payments
    def computeDebtPayments(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        toPay = 0
        totPrincipal = 0
        totInterests = 0
        
        for loan in self.loan_sheet:
            age = loan['Age'] #When is age updated
            if age > 0 and age <= Parameters.Loans_duration:
                assert loan['Value'] > 0
                amount = loan['InitialAmount']
                principal = amount/Parameters.Loans_duration
                assert principal > 0

                iRate = loan['InterestRate']
                value = loan['Value']
                interests = iRate*value
                assert interests > 0

                toPay += (principal + interests)
                totPrincipal += principal
                totInterests += interests
        
        assert toPay >= 0
        assert totPrincipal >= 0
        assert totInterests >= 0

        self.debtBurden = toPay
        self.debtPrincipal = totPrincipal
        self.debtInterests = totInterests
        

        #Notice that loans have to be changed to dictionaries: 
        #   {'InitialAmount':a, 'Age': b, 'InterestRate':c, 'Value':d, 'ID':e, 'Bank':f}
    
    #Compute credit demand
    def computeCreditDemand(self):
        # #First Method
        # """
        # Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        # """
        
        # self.computeDebtPayments()
        # totalFinancialRequirement = 0
        # nbWorkers = self.requiredWorkers
        # expWages = self.exp_avg_wage
        # totalFinancialRequirement = (nbWorkers*expWages
        #                             + self.desiredRealCapitalDemand*self.selectedSupplier.price #Must define self.selectedSupplier
        #                             + self.debtBurden - 'NumericBalanceSheet')  #<- !!!
        # self.creditDemanded = totalFinancialRequirement
        # if self.creditDemanded > 0:
        #     self.active['MKT_CREDIT'] = True

        #Second method
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirmWagesEnd
        """
        self.computeDebtPayments()
        totalFinancialRequirement = 0
        shareOfExpIncomeAsDeposit = Parameters.Precautionary_deposits_share #Not in source code
        expRevenues = self.exp_revenue
        expRealSales = self.exp_sales
        inv = self.inventories
        uc = self.unit_cost_present
        nbWorkers = self.requiredWorkers
        expWages = self.exp_avg_wage
        profitShare = Parameters.Firms_dividends_share
        profitTaxRate = Parameters.Profit_tax_rate
        shareInventories = Parameters.Inventories_target_share
        capitalAmortization = self.computeAmortisation() #There is a difference with source code, as the source code has not updated the age of the capital.
        expectedProfits = (expRevenues + self.interest_on_deposits
                            - (nbWorkers*expWages) - self.debtInterests
                            + (shareInventories*expRealSales - inv)*uc
                            - capitalAmortization)
        expectedTaxes = expectedProfits*profitTaxRate #What if negative?
        expectedDividends = expectedProfits*(1 - profitTaxRate)*profitShare #What if negative?
        Inv = self.desiredRealCapitalDemand*self.selectedSupplier.price #Must define self.selectedSupplier
        totalFinancialRequirement = ((nbWorkers*expWages)
                                    + Inv
                                    + self.debtBurden - self.interest_on_deposits
                                    + expectedTaxes + expectedDividends
                                    - expRevenues + shareOfExpIncomeAsDeposit*(nbWorkers*expWages))
        self.creditDemanded = totalFinancialRequirement #!!! See source code
        if self.creditDemanded > 0:
            self.active['MKT_CREDIT'] = True

    #Calculate labor demand
    def computeLaborDemand(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirmWagesEnd
        """
        currentWorkers = len(self.employees)
        employees_list = self.employees[:]
        # random.shuffle(employees_list) #Not in source code
        nTurnover = round(currentWorkers*Parameters.L_turnover_ratio)
        for i in range(nTurnover):
            employee = employees_list.pop()
            employee.employer = None
            self.employees.remove(employee)
        
        currentWorkers = len(self.employees)
        nbWorkers = self.requiredWorkers
        if nbWorkers > currentWorkers:
            laborDemand = nbWorkers - currentWorkers
        else:
            laborDemand = 0
            if currentWorkers > nbWorkers:
                extraWorkers = currentWorkers - nbWorkers
                for i in range(extraWorkers):
                    employee = self.employees.pop() #Notice that the last-hired-employee is fired.
                    employee.employer = None
                assert len(self.employees) == nbWorkers
        if laborDemand > 0:
            self.active['MKT_LABOR'] = True
        else:
            self.active['MKT_LABOR'] = False
        assert laborDemand >= 0
        self.laborDemand = laborDemand
        
        #There is an additional part that seems to be the wage payment, but what about the order of events?
    
    #Compute and update nominal capital value
    def updateCapitalValue(self):
        for capital in self.K_sheet:
            age = capital['Age']
            assert age <= Parameters.K_goods_duration
            initialValue = capital['Quantity']*capital['Price']
            depreciation = initialValue*age/Parameters.K_goods_duration
            currentValue = initialValue - depreciation
            assert currentValue >= - Parameters.Precision
            currentValue = max(0, currentValue)
            capital['Value'] = currentValue

    #Production
    def produce(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        outputQty = 0
        capacity = 0
        capValue = 0
        for capital in self.K_sheet:
                capacity += capital['Quantity']*Parameters.K_productivity
                capValue += capital['Value']
        self.pastCapitalValue = capValue
        self.updateCapitalValue()
        if len(self.employees) > 0:
            residualWorkers = len(self.employees)
            for capital in self.K_sheet:
                employedWorkers = capital['Quantity']/Parameters.K_L_ratio
                if employedWorkers < residualWorkers:
                    outputQty += capital['Quantity']*Parameters.K_productivity
                    residualWorkers -= employedWorkers
                else:
                    outputQty += residualWorkers*Parameters.K_L_ratio*Parameters.K_productivity
                    residualWorkers = 0
            inventories_past = self.inventories #Not in original code
            self.inventories = (outputQty + self.inventories_past)
            amortisationCosts = self.computeAmortisation()
            wageBill = self.computeWageBill()
            unit_cost_past = self.unit_cost_present #Not in original code
            self.unit_cost_present = (amortisationCosts + wageBill)/outputQty
        else:
            inventories_past = self.inventories #Not in original code
            unit_cost_past = self.unit_cost_present #Not in original code
        if self.inventories > 0:
            self.active['MKT_CONSGOOD'] = True
        else:
            self.active['MKT_CONSGOOD'] = False
        
        self.output = outputQty
    
        self.passedValues = {} #Not in original code
        self.passedValues['amortisationCosts'] = self.computeAmortisation() #Not in original code
        self.passedValues['wageBill'] = self.computeWageBill() #Not in original code
        self.passedValues['pastInventories'] = inventories_past #Not in original code
        self.passedValues['pastUnitCost'] = unit_cost_past #Not in original code
        self.passedValues['numberOfWorkers'] = len(self.employees) #Not in original code
    
    #Pay Wages
    def payWages(self, households):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirmWagesEnd
        """
        if len(self.employees) > 0:
            wageBill = self.computeWageBill()
            neededDiscount = 1
            if wageBill > self.deposits:
                neededDiscount = self.deposits/wageBill
            if neededDiscount < Parameters.minWageDiscount: #What is Parameters.minWageDiscount???
                currentWorkers = len(self.employees)
                #random.shuffle(len(self.employees)) What is prng???
                for employee in self.employees:
                    amountToPay = wageBill*neededDiscount/currentWorkers
                    amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = employee, output = True)
                    employee.income += amountToPay
                    employee.wagePayment += amountToPay
                assert abs(self.deposits) <= Parameters.Precision #Not in source code
                self.deposits = 0
                print('Default ' + str(self.id) + ' due to wages')
                self.bankruptcy(households)
            else:
                currentWorkers = len(self.employees)
                #random.shuffle(len(self.employees)) What is prng???
                for employee in self.employees:
                    amountToPay = employee.res_wage*neededDiscount
                    amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = employee, output = True)
                    employee.income += amountToPay
                    employee.wagePayment += amountToPay

    #Pay Interests (First interests or first wages ???, if interests after wages, must add if condition on default)
    def payInterests(self, households):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        self.computeDebtPayments()
        liquidity = self.deposits
        assert liquidity >= 0
        if liquidity >= self.debtBurden:
            for loan in self.loan_sheet:
                age = loan['Age']
                if age > 0 and age <= Parameters.Loans_duration:
                    assert loan['Value'] > 0
                    amount = loan['InitialAmount']
                    principal = amount/Parameters.Loans_duration
                    assert principal > 0

                    iRate = loan['InterestRate']
                    value = loan['Value']
                    interests = iRate*value
                    assert interests > 0

                    amountToPay = principal + interests
                    amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = loan['Bank'], output = True)
                    loan['Bank'].interestsPayment += interests
                    loan['Value'] -= principal
                    assert loan['Value'] >= - Parameters.Precision
                    loan['Value'] = max(0, loan['Value'])
        else:
            print('Default ' + str(self.id) + ' due to debt service')
            self.bankruptcy(households)

    #Bankruptcy
    def bankruptcy(self, households):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        self.defaulted = True
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\FirmBankruptcyFireSales
        """
        #Move all money on one deposit if there were two of them; Why?
        #Transfer all cash on the deposit account; Why?
        liquidity = self.deposits
        assert liquidity >= 0
        banksLosses = {}
        totalDebt = 0
        totalBanksLoss = 0
        for loan in self.loan_sheet:
            age = loan['Age']
            if age <= Parameters.Loans_duration
                totalDebt += loan['Value']
                totalBanksLoss += loan['Value']
                banksLosses[str(loan['ID'])] = loan['Value']
        if totalDebt != 0:
            for loan in self.loan_sheet:
                age = loan['Age']
                if age <= Parameters.Loans_duration
                    amountToPay = liquidity*loan['Value']/totalDebt
                    if liquidity >= totalDebt:
                        amountToPay = loan['Value']
                    amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = loan['Bank'], output = True)
                    loan['Value'] -= amountToPay
                    assert loan['Value'] >= - Parameters.Precision
                    loan['Value'] = max(0, loan['Value'])
                    banksLosses[str(loan['ID'])] -= amountToPay
                    assert banksLosses[str(loan['ID'])] >= - Parameters.Precision
                    banksLosses[str(loan['ID'])] = max(0, banksLosses[str(loan['ID'])])
                    totalBanksLoss -= amountToPay
                    assert totalBanksLoss >= - Parameters.Precision
                    totalBanksLoss = max(0, totalBanksLoss)
            assert abs(self.deposits) <= Parameters.Precision
            self.deposits = 0
            #For Cfirms
            capitalValue = 0
            for capital in self.K_sheet:
                capitalValue = capital['Value']*Parameters.Haircut_deafaulted_K_value
            ownersDisbursment = 0
            if capitalValue > totalBanksLoss:
                ownersDisbursment = totalBanksLoss
            else:
                ownersDisbursment = capitalValue
            self.bailoutCost = ownersDisbursment
            totalHouseholdWealth = 0
            for household in households:
                totalHouseholdWealth += household.netWealth #Define household.netWealth as equal to deposits at a certain point
            for household in households:
                householdNetWealth = household.netWealth #Define household.netWealth as equal to deposits at a certain point
                for loan in self.loan_sheet:
                    amountToPay = ((ownersDisbursment*householdNetWealth/totalHouseholdWealth)
                                    *(banksLosses[str(loan['ID'])]/totalBanksLoss))
                    amountToPay = Transaction.transaction(amount = amountToPay, payer = household, receiver = loan['Bank'], output = True)
                    loan['Value'] -= amountToPay
                    assert loan['Value'] >= - Parameters.Precision
                    loan['Value'] = max(0, loan['Value'])
                    banksLosses[str(loan['ID'])] -= amountToPay
                    assert banksLosses[str(loan['ID'])] >= - Parameters.Precision
                    banksLosses[str(loan['ID'])] = max(0, banksLosses[str(loan['ID'])])
                    totalBanksLoss -= amountToPay
                    assert totalBanksLoss >= - Parameters.Precision
                    totalBanksLoss = max(0, totalBanksLoss)
            # For all firms
            for loan in self.loan_sheet:
                assert abs(banksLosses[str(loan['ID'])]) >= - Parameters.Precision
                banksLosses[str(loan['ID'])] = max(0, banksLosses[str(loan['ID'])])
                loan['Bank'].currentNonPerformingLoans += banksLosses[str(loan['ID'])]
                assert loan['Value'] >= - Parameters.Precision
                loan['Value'] = 0
        for employee in self.employees:
            employee.employer = None
        self.employees = []
        self.deposits_bank.deposits_list.remove(self)
        self.deposits = 0 #!!!
        # Create new set of asset ???
        # What if no totalDebt, what happens to deposits???
    
    #Update before-tax profits
    def updatePreTaxProfits(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        pastInventories = self.passedValues['pastInventories']
        pastUnitCost = self.passedValues['pastUnitCost']
        lNomInv = pastInventories*pastUnitCost
        assert lNomInv >= 0
        nomInv = self.inventories*self.unit_cost_present
        assert nomInv >= 0
        revenue = self.revenue
        wageBill = self.passedValues['wageBill'] #Not in original code
        amortisationCosts = self.passedValues['amortisationCosts'] #Not in original code
        self.profits = (revenue + self.interest_on_deposits
                        + nomInv - lNomInv
                        - wageBill - amortisationCosts
                        - self.debtInterests)

    #Pay Taxes
    def payTaxes(self, households, gov):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        self.updatePreTaxProfits()
        taxes = 0
        if self.defaulted != True:
            taxes = max(0, self.profits*Parameters.Profit_tax_rate) #Not in source code
        else:
            taxes = 0
        self.passedValues['Taxes'] = taxes #Not in source code
        liquidity = self.deposits
        assert liquidity >= 0
        if taxes > liquidity:
            print('Default ' + str(self.id) + ' due to taxes')
            self.bankruptcy(households)
            self.tax = 0
        else:
            amountToPay = taxes
            amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = gov, output = True)
            gov.tax_payment += amountToPay
            self.tax = amountToPay
            self.passedValues['Taxes'] = amountToPay

    #Update after-tax profits
    def updateAfterTaxProfits(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\ConsumptionFirm
        """
        taxes = self.passedValues['Taxes']
        profitsAfterTaxes = self.profits - taxes
        self.profits_post_tax = profitsAfterTaxes
        operatingNetCashFlow = 0
        capitalAmortization = self.passedValues['amortisationCosts']
        pastInventories = self.passedValues['pastInventories']
        pastUnitCost = self.passedValues['pastUnitCost']
        lNomInv = pastInventories*pastUnitCost
        assert lNomInv >= 0
        nomInv = self.inventories*self.unit_cost_present
        assert nomInv >= 0
        varInv = nomInv - lNomInv
        principal = self.debtPrincipal
        operatingNetCashFlow = profitsAfterTaxes + capitalAmortization - varInv - principal
        self.OCF = operatingNetCashFlow

     #Pay dividends
     def payDividends(self, households):
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\FixedShareOfProfitsToPopulationAsShareOfWealthDividends
        """
        if self.defaulted != True:
            profits = self.profits_post_tax
            self.dividend_disbursement = 0
            if profits > 0:
                totalNW = 0
                for household in households:
                    totalNW += household.netWealth #Define household.netWealth as equal to deposits at a certain point
                liquidity = self.deposits
                if liquidity > profits*Parameters.Firms_dividends_share:
                    for household in households:
                        amountToPay = profits*Parameters.Firms_dividends_share*household.netWealth/totalNW
                        amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = household, output = True)
                        self.dividend_disbursement += amountToPay
                        household.income += amountToPay
                        household.dividendsReceived += amountToPay

    #Compute Liquid Assets Amounts
    def computeLiquidAssetsAmounts(self):
        assert self.deposits >= - Parameters.Precision
        self.deposits = max(0, self.deposits)
        self.active['MKT_DEPOSIT'] = True
    
    def getCapitalValue(self):
        totCapitalValue = 0
        for capital in self.K_sheet:
            age = capital['Age']
            assert age <= Parameters.K_goods_duration
            capitalValue = capital['Value']
            assert capitalValue >= 0
            totCapitalValue += capitalValue
        assert totCapitalValue >= 0
        return totCapitalValue

    #Compute outstanding debt
    def getOutstandingDebt(self):
        totDebt = 0
        for loan in self.loan_sheet:
            age = loan['Age']
            if age <= Parameters.Loans_duration:
                assert loan['Value'] >= 0
                totBebt += loan['Value']
        assert totBebt >= 0
        return totBebt


    #Compute Net Wealth
    def getNetWealth(self):
        """
        Source: jmab\src\jmab\agents\SimpleAbstractAgent
        """
        assets = self.deposits
        assets += self.inventories*self.unit_cost_present
        assets += self.getCapitalValue()
        assert assets >= 0
        liabilities = self.getOutstandingDebt()
        assert liabilities >= 0
        netWealth = assets - liabilities
        return netWealth

    #Update expectations:
    def updateExpectations(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\CapitalFirm
        """
        revenue = self.revenue
        self.exp_revenue = expectation(revenue, self.exp_revenue)
        realSales = self.sales
        self.exp_sales = expectation(realSales, self.exp_sales)
        numberOfWorkers = self.passedValues['numberOfWorkers'] #Not in original code
        wageBill = self.passedValues['wageBill'] #Not in original code
        if numberOfWorkers > 0:
            avgWage = wageBill/numberOfWorkers
        else:
            avgWage = self.exp_avg_wage
        assert avgWage > 0
        self.exp_avg_wage = expectation(avgWage, self.exp_avg_wage)
        netWealth = self.getNetWealth()
        self.exp_net_wealth = expectation(netWealth, self.exp_net_wealth)