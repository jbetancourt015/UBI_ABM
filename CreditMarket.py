import Parameters
import random
import numpy as np
import Transaction

#Evaluation function for credit approval
def loan_evaluation(firm, bank, amount):
    varsigma_c = Parameters.Banks_C_risk_aversion
    varsigma_k = Parameters.Banks_K_risk_aversion
    iota = Parameters.Haircut_deafaulted_K_value
    debt_service = (bank.r_loans + 1/Parameters.Loans_duration)*amount
    
    if firm.type == 'C':
        p_default = (np.exp(-(firm.OCF-varsigma_c*debt_service)/debt_service)/
                     (1+np.exp(-(firm.OCF-varsigma_c*debt_service)/debt_service)))
        discounted_value = 0
        for element in firm.K_sheet:
            discounted_value += (1-iota)*element[3]
    else:
        p_default = (np.exp(-(firm.OCF-varsigma_k*debt_service)/debt_service)/
                     (1+np.exp(-(firm.OCF-varsigma_k*debt_service)/debt_service)))
        discounted_value = 0
    
    total_outstanding_debt = 0
    
    if len(firm.loan_sheet) > 0:
        for element in firm.loan_sheet:
            total_outstanding_debt += element[3]
    
    delta = min(1,discounted_value/(total_outstanding_debt+amount))
    exp_return = p_default*(delta-1)*amount
    
    for n in range(Parameters.Loans_duration-1):
        interest_payment = 0
        for i in range(n+1):
            interest_payment += bank.r_loans*amount*(1-(i/Parameters.Loans_duration))
        exp_return += ((1-p_default)**(n+1))*p_default*(interest_payment+(delta-1)*
                        (1-((n+1)/Parameters.Loans_duration))*amount)
    
    final_payment = 0
    
    for n in range(Parameters.Loans_duration):
        final_payment += bank.r_loans*amount*(1-(n/Parameters.Loans_duration))
    exp_return += ((1-p_default)**(Parameters.Loans_duration))*final_payment
    
    return exp_return

#Firms choose their lending bank
def matching(Kfirms, Cfirms, banks):
    demand_firms = []
    N_partners = Parameters.N_partners_credit_market
    e_credit = Parameters.Choice_intensity_credit_market
    epsilon = 0.001
    
    for cfirm in Cfirms:
        cfirm.loan_granted = 0
        if cfirm.loan_requirement > 0:
            demand_firms.append(cfirm)
    
    for kfirm in Cfirms:
        kfirm.loan_granted = 0
        if kfirm.loan_requirement > 0:
            demand_firms.append(kfirm)
            
    random.shuffle(demand_firms)
    
    for firm in demand_firms:
        opt = []
        random.shuffle(banks)
        
        for bank in banks:
            if bank != firm.old_bank:
                opt.append(bank)
            if len(opt)==N_partners:
                break
            
        options = []
        
        for bank in opt:
            options.append([bank.r_loans,bank])
            
        options.sort(key=lambda x: int(x[0]),reverse = True)
        new_bank_list = options.pop()
        new_bank = new_bank_list[1]
        diff = new_bank.r_loans/firm.old_bank.r_loans - 1
        if diff < 0:
            p_switch = 1-np.exp(e_credit*diff)
            switch = np.random.choice([0,1],p=[1-p_switch,p_switch])
            if switch == 0:
                new_bank = firm.old_bank
        else:
            new_bank = firm.old_bank
        firm.old_bank = new_bank
    
def transactions(Kfirms, Cfirms, banks):
    demand_firms = []
    N_partners = Parameters.N_partners_credit_market
    e_credit = Parameters.Choice_intensity_credit_market
    epsilon = 0.001
    
    for cfirm in Cfirms:
        cfirm.loan_granted = 0
        if cfirm.loan_requirement > 0:
            demand_firms.append(cfirm)
    
    for kfirm in Cfirms:
        kfirm.loan_granted = 0
        if kfirm.loan_requirement > 0:
            demand_firms.append(kfirm)
            
    random.shuffle(demand_firms)

    for firm in demand_firms:
        if loan_evaluation(firm, firm.old_bank, firm.loan_requirement) >= 0:
            new_loan = firm.loan_requirement
            new_loan = Transaction.transaction(amount = new_loan, payer = firm.old_bank, receiver = firm, output = True)
            
            firm.old_bank.loan_number += 1
            loan_ID = str(firm.old_bank.id)+'_'+str(firm.old_bank.loan_number)
            firm.loan_sheet.append([new_loan,0,firm.old_bank.r_loans,new_loan,
                                    loan_ID,firm.old_bank])
            firm.old_bank.loan_sheet.append([new_loan,0,firm.old_bank.r_loans,new_loan,
                                             loan_ID,firm])
            firm.loan_granted += new_loan
            
        else:
            high = firm.loan_requirement
            assert high >= - Parameters.Precision
            high = max(0, high)
            low = 0
            while True:
                amount = (high+low)/2
                assert amount >= - Parameters.Precision
                amount = max(0, amount)
                try:
                    eps = loan_evaluation(firm,firm.old_bank,amount)
                except ZeroDivisionError:
                    break
                else:
                    if eps > epsilon:
                        low = amount
                    elif eps < 0:
                        high = amount
                    else:
                        if amount > 0:
                            new_loan = firm.loan_requirement
                            new_loan = Transaction.transaction(amount = new_loan, payer = firm.old_bank, receiver = firm, output = True)
            
                            firm.old_bank.loan_number += 1
                            loan_ID = str(firm.old_bank.id)+'_'+str(firm.old_bank.loan_number)
                            firm.loan_sheet.append([new_loan,0,firm.old_bank.r_loans,new_loan,
                                                    loan_ID,firm.old_bank])
                            firm.old_bank.loan_sheet.append([new_loan,0,firm.old_bank.r_loans,new_loan,
                                                              loan_ID,firm])
                            
                            firm.loan_granted += new_loan
                            
                            break
                        else:
                            break