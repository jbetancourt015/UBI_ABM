#Used packages and files
import Parameters
import numpy as np
import Transaction
import Households

class Bank(object):
    
    def __init__(self, identification, r_loans, r_deposits, reserves, loan_number, bonds,
                 net_worth, cash_advances, liquidity_ratio=None,
                 capital_ratio=None, interest_payment=None, 
                 profit_post_tax=None, bond_demand=None, cash_demand=None):
        
        self.id = 'B_' + str(identification)
        self.iRateLoans = r_loans
        self.iRateDeposits = r_deposits
        self.reserves = reserves
        self.loan_number = loan_number
        self.bonds = bonds
        self.net_worth = net_worth
        self.cash_advances = cash_advances
        self.liquidityRatio = liquidity_ratio
        self.capitalRatio = capital_ratio
        self.interest_payment = interest_payment
        self.profit_post_tax = profit_post_tax
        self.bond_demand = bond_demand
        self.cash_demand = cash_demand
        self.loan_sheet = []
        self.deposits_list = []

    #Set bailout cost
    def setBailoutCost(self, amount):
        """
        Source: \benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        assert amount >= 0
        self.bailoutCost = amount
    
    #Set non performing loans
    def setCurrentNonPerformingLoans(self, amount):
        """
        Source: \benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        assert amount >= 0
        self.currentNonPerformingLoans = amount

    #Compute deposits
    def computeDeposits(self):
        depositsValue = 0
        for agent in self.deposits_list:
            assert agent.deposits >= - Parameters.Precision
            agent.deposits = max(0, agent.deposits)
            depositsValue += agent.deposits
        assert depositsValue >= 0
        return depositsValue
        
    #Compute liquidity ratio
    def computeLiquidityRatio(self, Set = True, output = False):
        """
        Source: \benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        depositsValue = self.computeDeposits()
        reservesValue = self.reserves
        if depositsValue == 0:
            liquidityRatio = 0
        else:
            liquidityRatio = reservesValue/depositsValue
        if Set == True:
            self.liquidityRatio = liquidityRatio
        if output == True:
            return liquidityRatio

    #Compute outstanding loans
    def computeOutstandingLoans(self): #Must change
        outstandingLoansValue = 0
        for element in self.loan_sheet: #Must be list of dictionaries : [{'ID':loanID , 'Debtor':debtor}, ...]
            loanID = element['ID']
            debtor = element['Debtor']
            for loan in debtor.loan_sheet:
                if loan['ID'] == loanID:  
                    assert loan['Value'] >= 0
                    outstandingLoansValue += loan['Value']
        assert outstandingLoansValue >= 0
        return outstandingLoansValue

    #Compute capital ratio
    def computeCapitalRatio(self, Set = True, output = False):
        """
        Source: \benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        outstandingLoansValue = self.computeOutstandingLoans()
        netWealth = self.passedValues['NetWealth'] #Must define this dictionary
        if outstandingLoansValue == 0:
            capitalRatio = float('inf')
        else:
            capitalRatio = netWealth/outstandingLoansValue
        if Set == True:
            self.capitalRatio = capitalRatio
            if self.capitalRatio == float('inf'):
                self.capitalRatio = None
        if output == True:
            return capitalRatio
    
    #Compute bonds
    def computeBonds(self):
        totBonds = 0
        for bond in self.bonds: #Each bond is a dictionary {'Quantity':a, 'Age':b, 'Price':c, 'Value':d}
            assert bond['Value'] >= 0
            totBonds += bond['Value']
        return totBonds
    
    #Compute cash advances
    def computeCashAdvances(self):
        totCashAdvances = 0
        for cashAdvance in self.cashAdvances: #Each cash advance is a dictionary
            assert cashAdvance['Value'] >= 0
            totCashAdvances += cashAdvance['Value']
        return totCashAdvances

    #Payment of interests on deposits
    def payDepositInterests(self):
        """
        Source: \benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        totInterests = 0
        for agent in self.deposits_list:
            assert agent.deposits >= - Parameters.Precision
            agent.deposits = max(0, agent.deposits)
            amountToPay = self.iRateDeposits*agent.deposits #Define self.iRateDeposits
            amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = agent, output = True)
            agent.interest_on_deposits = amountToPay
            if type(agent) == Households.Household:
                agent.income += amountToPay
            totInterests += amountToPay
        self.totInterestsDeposits = totInterests
    
    #Get reference variable for interest rate
    def getReferenceVariableForInterestRate(self, mkt):
        if mkt == 'MKT_CREDIT':
            referenceVariable = self.computeCapitalRatio(Set = False, output = True)
        elif mkt == 'MKT_DEPOSIT':
            referenceVariable = self.computeLiquidityRatio(Set = False, output = True)
        return referenceVariable

    #Determine loan interest rate
    def determineLoanInterestRate(self, targetedCapitalRatio, averageIRateLoans): #Name in source: determineBankGenericInterestRate()
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\CopyOfAdaptiveInterestRateAverageThreshold
        """
        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        referenceVariable = self.getReferenceVariableForInterestRate(mkt = 'MKT_CREDIT')
        iR = 0
        threshold = targetedCapitalRatio
        if referenceVariable < threshold:
            change = abs(np.random.normal(FNmean,FNsd))
            iR = averageIRateLoans*(1 + change)
        else:
            change = abs(np.random.normal(FNmean,FNsd))
            while change >= 1:
                change = abs(np.random.normal(FNmean,FNsd))
            iR = averageIRateLoans*(1 - change) 
        assert iR > 0
        self.iRateLoans = iR

        #Check This source for targetedCapitalRatio and averageIRateLoans calculation
    
    #Determine deposits interest rate
    def determineDepositInterestRate(self, targetedLiquidityRatio, averageIRateDeposits):
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\CopyOfAdaptiveInterestRateAverageThreshold
        """
        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        referenceVariable = self.getReferenceVariableForInterestRate(mkt = 'MKT_DEPOSIT')
        iR = 0
        threshold = targetedLiquidityRatio
        if referenceVariable < threshold:
            change = abs(np.random.normal(FNmean,FNsd))
            iR = averageIRateDeposits*(1 + change)
        else:
            change = abs(np.random.normal(FNmean,FNsd))
            while change >= 1:
                change = abs(np.random.normal(FNmean,FNsd))
            iR = averageIRateDeposits*(1 - change)   
        assert iR > 0
        self.iRateDeposits = min(iR, Parameters.CB_i_advances)
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        self.active['MKT_DEPOSIT'] = True

        #Check This source for targetedLiquidityRatio and averageIRateDeposits calculation
    
    #Determine credit supply
    def determineCreditSupply(self):
        #Not clear in benchmark model, will select the infinite supply version in JMAB
        """
        Source: jmab\src\jmab\strategies\InfiniteSupplyCreditStrategy
        """
        self.totalLoansSupply = float('inf')
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        if self.totalLoansSupply > 0:
            self.active['MKT_CREDIT']
    
    #Payment of cash advance interests
    def payInterests(self, cb):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        totPrincipal = 0
        totInterests = 0
        toPay = 0
        for cashAdvance in self.cashAdvances: #List for cash advances
            age = cashAdvance['Age']
            if age > 0 and age <= Parameters.Cash_advance_duration:
                assert cashAdvance['Value'] > 0
                amount = cashAdvance['InitialAmount']
                principal = amount/Parameters.Cash_advance_duration
                assert principal > 0

                iRate = cashAdvance['InterestRate']
                value = cashAdvance['Value']
                interests = iRate*value
                assert interests > 0

                amountToPay = principal + interests
                self.reserves -= amountToPay
                cb.interestsCashAdvances += interests
                cashAdvance['Value'] -= principal
                assert cashAdvance['Value'] >= - Parameters.Precision
                cashAdvance['Value'] = max(0, cashAdvance['Value'])

                totPrincipal += principal
                totInterests += interests
                toPay += amountToPay
        assert toPay >= 0
        assert totPrincipal >= 0
        assert totInterests >= 0

        self.debtBurden = toPay
        self.debtPrincipal = totPrincipal
        self.debtInterests = totInterests
    
    #Compute Net Wealth
    def getNetWealth(self):
        """
        Source: jmab\src\jmab\agents\SimpleAbstractAgent
        """
        assets = self.reserves
        assets += self.computeBonds()
        assets += self.computeOutstandingLoans()
        assert assets >= 0
        liabilities = self.computeDeposits()
        liabilities += self.computeCashAdvances()
        assert liabilities >= 0
        netWealth = assets - liabilities
        return netWealth

    #Determine Bankruptcy
    def determineBankruptcy(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        netWealth = self.getNetWealth()
        if netWealth < 0:
            print('Default ' + str(self.id))
            self.bankruptcy()
    
    #Bankruptcy
    def bankruptcy(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        self.defaulted = True
        #Not sure what strategy to use. From paper, could be the following:
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\BankBankruptcyBailout
        """
        netWealth = self.getNetWealth()
        assert netWealth < 0
        self.setBailoutCost(- netWealth)
        bailoutCost = self.bailoutCost
        assert bailoutCost == - netWealth
        totDeposits = self.computeDeposits()
        reserves = self.reserves
        for agent in self.deposits_list:
            amountToTransfer = agent.deposits*bailoutCost/totDeposits
            amountToTransfer = Transaction.transaction(amount = amountToTransfer, payer = agent, receiver = self, output = True)
        assert abs(self.reserves - reserves) <= Parameters.Precision
        #There are some expectations involved, but I don't know why
    
    #Determine bond demand
    def determineBondDemand(self, targetedLiquidityRatio, banks, gov):
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\BondDemandStrategyReserves
        """
        liquidityRatio = targetedLiquidityRatio #What is this target???
        employableReserves = 0
        for bank in banks:
            depositsValue = bank.computeDeposits()
            reservesValue = bank.reserves
            employableReserves += max(0, reservesValue - liquidityRatio*depositsValue)
        assert employableReserves >= 0
        bankDeposits = self.computeDeposits()
        bankReserves = self.reserves
        bondsPrice = gov.bondPrice #<- Set this for government
        if employableReserves/bondsPrice >= gov.bondSupply: #<- Set this for government
            demand = round(gov.bondSupply*max(0, bankReserves - liquidityRatio*bankDeposits)/employableReserves)
        else:
            demand = round(max(0, bankReserves - liquidityRatio*bankDeposits)/bondsPrice)
        assert demand >= 0
        self.bondDemand = demand
        if self.bondDemand > 0:
            self.active['MKT_BONDS']
    
    #Pay taxes
    def payTaxes(self, gov):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        netWealth = self.getNetWealth()
        profitsPreTax = netWealth - self.passedValues['NetWealth']
        self.profits = profitsPreTax
        taxes = 0
        if self.defaulted != True:
            taxes = max(0, self.profits*Parameters.Profit_tax_rate) #Not in source code
        else:
            taxes = 0
        self.passedValues['Taxes'] = taxes #Not in source code
        self.tax = taxes
        self.reserves -= taxes
        gov.reserves += taxes
        gov.tax_payment += taxes
    
    #Pay Dividends
    def payDividends(self, households):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        netWealth = self.getNetWealth()
        profitsAfterTaxes = netWealth - self.passedValues['NetWealth']
        self.profits_post_tax = profitsAfterTaxes
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\FixedShareOfProfitsToPopulationAsShareOfWealthDividends
        """
        totalNW = 0
        for household in households:
            totalNW += household.netWealth #Define household.netWealth as equal to deposits at a certain point
        self.dividend_disbursement = 0
        profits = profitsAfterTaxes
        if profits > 0:
            for household in households:
                amountToPay = profits*Parameters.Banks_dividends_share*household.netWealth/totalNW
                amountToPay = Transaction.transaction(amount = amountToPay, payer = self, receiver = household, output = True)
                self.dividend_disbursement += amountToPay
                household.income += amountToPay
                household.dividendsReceived += amountToPay

    #Determine cash advances demand Basel
    def determineAdvancesDemandBasel(self, targetedliquidityRatio):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        depositsValue = self.computeDeposits()
        reservesValue = self.reserves
        cashAdvanceDemand = targetedLiquidityRatio*depositsValue - reservesValue
        self.advancesDemand = cashAdvanceDemand
        if self.advancesDemand > 0:
            self.active['MKT_ADVANCES']
    
    #Update expectations
    def updateExpectations(self):
        """
        Source: benchmark-master\benchmark\src\benchmark\agents\Bank
        """
        netWealth = self.getNetWealth()
        self.passedValues['NetWealth'] = netWealth
        
    #Get loan supply (specific)
    def getLoanSupply(self, creditDemander, required, Cfirms, Kfirms, binaryDecision):
        #Two methods, the one suggested by the source, the other by the paper
        #Method 1:
        """
        Source: benchmark-master\benchmark\src\benchmark\strategies\MaxExposureStrategyDifferentiated
        """
        totalExposure = 0
        exposureToCreditDemander = 0
        for element in self.loan_sheet:
            loanID = element['ID']
            debtor = element['Debtor']
            for loan in debtor.loan_sheet:
                if loan['ID'] == loanID and loan['Age'] != 0:  
                    assert loan['Value'] >= 0
                    totalExposure += loan['Value']
                    if debtor == creditDemander:
                        exposureToCreditDemander += loan['Value']
        CfirmsSize = len(Cfirms)
        KfirmsSize = len(Kfirms)
        if creditDemander in Kfirms:
            return max(0, (totalExposure*maxShareTotalLoans*KfirmsSize/CfirmsSize) - exposureToCreditDemander)
        else:
            return max(0, (totalExposure*maxShareTotalLoans) - exposureToCreditDemander)
        #Method 2:
        """
        Source: jmab\src\jmab\strategies\ExpectedReturnCreditSupply
        """
        totCurrentDebt = 0
        capitalValue = 0
        for loan in creditDemander.loan_sheet:
            totCurrentDebt += loan['Value']
        if creditDemander in Cfirms:
            for capital in creditDemander.K_sheet:
                #Not sure which should be used, this...
                age = capital['Age']
                assert age <= Parameters.K_goods_duration
                initialValue = capital['Quantity']*capital['Price']
                depreciation = initialValue*age/Parameters.K_goods_duration
                newValue = initialValue - depreciation
                assert newValue >= - Parameters.Precision
                newValue = max(0, newValue)
                capitalValue += newValue*Parameters.Haircut_deafaulted_K_value
                #Or this... notice that this would be for non-updated capital value
                # capitalValue += capital['Value']
        expectedShareRecovered = min(1, capitalValue/totCurrentDebt)
        duration = Parameters.Loans_duration
        shareRepaid = 1/duration
        interest = self.iRateLoans
        amount = 0
        for i in range(101):
            amount = required*(1 - i/100)
            assert amount >= 0
            probability = self.getDefaultProbability(creditDemander, amount) #Must define this function
            expectedReturn = 0
            for t in range(duration):
                expectedReturn += ((1-probability)**t)*(-1 + shareRepaid*t)*amount*(1 - expectedShareRecovered) + ((1-probability)**(t+1))*interest*amount
            for i in range(1, duration-1):
                expectedReturn += ((1-probability)**duration)*interest*amount*(duration - 0.5*(duration - 1)*shareRepaid*duration)
            if binaryDecision == True:
                if expectedReturn >= 0:
                    return required
                    break
                else:
                    return 0
                    break
            else:
                if expectedReturn >= 0:
                    return amount
                    break
                



        

        
        

        











    
    #Set the interest rate on loans
    def set_r_loans(self, avg_capital_ratio, avg_r_loans):
        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        total_loan = 0
        
        for element in self.loan_sheet:
            total_loan += element[3]
            
        deposits = 0
            
        for agent in self.deposits_list:
            deposits += agent.deposits
        
        self.net_worth = (self.reserves+total_loan+self.bonds*Parameters.Bonds_price-
                          deposits-self.cash_advances)
        if total_loan > 0:
            self.capital_ratio = self.net_worth/total_loan
        else:
            self.capital_ratio = 'no loans'
        
        if avg_capital_ratio != None:
            if avg_capital_ratio >= Parameters.Min_capital_ratio:
                if self.capital_ratio == 'no loans':
                    mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                    while mark_up <= 0:
                        mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                elif self.capital_ratio < avg_capital_ratio:
                    mark_up = 1 + abs(np.random.normal(FNmean,FNsd))
                else:
                    mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                    while mark_up <= 0:
                        mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
            else:
                if self.capital_ratio == 'no loans':
                    mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                    while mark_up <= 0:
                        mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                elif self.capital_ratio < Parameters.Min_capital_ratio:
                    mark_up = 1 + abs(np.random.normal(FNmean,FNsd))
                else:
                    mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                    while mark_up <= 0:
                        mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
        else:
            mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
            while mark_up <= 0:
                1 - abs(np.random.normal(FNmean,FNsd))
        self.r_loans = avg_r_loans*mark_up
                
    #Set the interest rate on deposits
    def set_r_deposits(self, avg_liquidity_ratio, avg_r_deposits):
        FNmean = Parameters.Folded_normal_mean
        FNsd = np.sqrt(Parameters.Folded_normal_variance)
        deposits = 0
        
        for agent in self.deposits_list:
            deposits += agent.deposits
        
        if deposits > 0:
            self.liquidity_ratio = self.reserves/deposits
        else:
            self.liquidity_ratio = 'no deposits'
            
        if avg_liquidity_ratio != None:
            if self.liquidity_ratio == 'no deposits':
                mark_up = 1 + abs(np.random.normal(FNmean,FNsd))
            elif self.liquidity_ratio < avg_liquidity_ratio:
                mark_up = 1 + abs(np.random.normal(FNmean,FNsd))
            else:
                mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
                while mark_up <= 0:
                    mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
        else:
            mark_up = 1 - abs(np.random.normal(FNmean,FNsd))
            while mark_up <= 0:
                1 - abs(np.random.normal(FNmean,FNsd))
        self.r_deposits = avg_r_deposits*mark_up

    #Tax payment
    def pay_taxes(self, gov):
        interest_on_deposits = 0
        
        for agent in self.deposits_list:
            interest_on_deposits += agent.interest_on_deposits

        profit_pre_tax = (self.interest_payment 
                          + self.interests_on_bonds 
                          - interest_on_deposits 
                          - self.interests_on_cash_transfers)
        
        self.tax = max(0, profit_pre_tax*Parameters.Profit_tax_rate)
        self.profit_post_tax = profit_pre_tax - self.tax

        self.reserves -= self.tax
        gov.reserves += self.tax
        gov.tax_payment += self.tax

    #Dividend payment
    def pay_dividends(self, households, total_wealth, total_wealth_pre):
        dividend_disbursement = max(0, Parameters.Banks_dividends_share*self.profit_post_tax)
        
        for household in households:
            amount = dividend_disbursement*household.deposits/total_wealth
            amount = Transaction.transaction(amount, payer = self, receiver = household, output = True)
            household.income += amount

        for household in households:
            amount = dividend_disbursement*household.wealth_pre/total_wealth_pre
            assert amount >= - Parameters.Precision
            amount = max(0, amount)
            household.wealth_pre += amount

    #Calculation of the demand for bonds and cash advances
    def calculate_bonds_and_cash_demand(self, avg_liquidity_ratio):
        deposits = 0
        
        for agent in self.deposits_list:
            assert agent.deposits >= - Parameters.Precision
            agent.deposits = max(0, agent.deposits)
            deposits += agent.deposits
        
        if deposits > 0:
            self.liquidity_ratio = self.reserves/deposits
        else:
            self.liquidity_ratio = 'no deposits'
        
        if self.liquidity_ratio != 'no deposits':
            if avg_liquidity_ratio != None:
                target_liquidity_ratio = max(avg_liquidity_ratio, Parameters.Min_liquidity_ratio)
            else:
                target_liquidity_ratio = Parameters.Min_liquidity_ratio
            desired_reserves = deposits*target_liquidity_ratio
            if self.reserves >= desired_reserves:
                self.bond_demand = (self.reserves - desired_reserves)/Parameters.Bonds_price
                self.cash_demand = 0
            else:
                self.bond_demand = 0
                self.cash_demand = desired_reserves - self.reserves
                
            assert self.bond_demand >= - Parameters.Precision
            self.bond_demand = max(0, self.bond_demand)
            assert self.cash_demand >= - Parameters.Precision
            self.cash_demand = max(0, self.cash_demand)
                
    #Accounting
    def accounting(self, avg_capital_ratio):
        total_loan = 0
        
        for element in self.loan_sheet:
            total_loan += element[3]
        
        deposits = 0
        
        for agent in self.deposits_list:
            deposits += agent.deposits
        
        self.net_worth = (self.reserves + total_loan + self.bonds*Parameters.Bonds_price 
                          - deposits - self.cash_advances)
        
        if total_loan > 0:
            self.capital_ratio = self.net_worth/total_loan
        else:
            self.capital_ratio = 'no loans'
        
        if self.capital_ratio != 'no loans':
            if self.capital_ratio < 0:
                assert self.net_worth < 0
                if avg_capital_ratio != None:
                    change = max(avg_capital_ratio, Parameters.Min_capital_ratio)*total_loan - self.net_worth
                else:
                    change = Parameters.Min_capital_ratio*total_loan - self.net_worth
                assert change >= - Parameters.Precision
                change = max(0, change)
                
                for agent in self.deposits_list:
                    assert agent.deposits_bank == self
                    amount = min(agent.deposits, change*agent.deposits/deposits)
                    Transaction.transaction(amount, payer = agent, receiver = self, output = False)















