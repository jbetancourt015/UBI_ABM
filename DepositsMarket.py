import Parameters
import random
import numpy as np

#Interests on deposits are paid
def interest_payment(households, banks):
    for bank in banks:
        for agent in bank.deposits_list:
            assert agent.deposits_bank == bank
            agent.deposits += agent.interest_on_deposits
            assert agent.deposits >= - Parameters.Precision
            agent.deposits = max(0, agent.deposits)
        if agent in households:
            agent.income += agent.interest_on_deposits

def matching(Kfirms, Cfirms, households, banks):
    demand_agents = []
    N_partners = Parameters.N_partners_deposit_market
    e_deposits = Parameters.Choice_intensity_deposits_market
    
    for household in households:
        demand_agents.append(household)
        
    for cfirm in Cfirms:
        demand_agents.append(cfirm)
        
    for kfirm in Kfirms:
        demand_agents.append(kfirm)
        
    random.shuffle(demand_agents)
    
    for agent in demand_agents:
        assert agent.deposits >= - Parameters.Precision
        agent.deposits = max(0, agent.deposits)

        opt = []
        random.shuffle(banks)
        
        for bank in banks:
            if bank != agent.deposits_bank:
                opt.append(bank)
            if len(opt) == N_partners:
                break
            
        options = []
        
        for bank in opt:
            options.append([bank.r_deposits, bank])
        
        options.sort(key=lambda x: int(x[0]))
        new_bank = options.pop()[1]
        diff = new_bank.r_deposits/agent.deposits_bank.r_deposits - 1
        
        if diff > 0:
            p_switch = 1 - np.exp(-e_deposits*diff)
            switch = np.random.choice([0,1], p=[1-p_switch,p_switch])
            if switch == 1:
                agent.deposits_bank.deposits_list.remove(agent)
                agent.deposits_bank.reserves -= agent.deposits
                agent.deposits_bank = new_bank
                agent.deposits_bank.deposits_list.append(agent)
                agent.deposits_bank.reserves += agent.deposits

        assert agent.deposits >= - Parameters.Precision
        agent.deposits = max(0, agent.deposits)
        agent.interest_on_deposits = agent.deposits_bank.r_deposits*agent.deposits
        assert agent.interest_on_deposits >= - Parameters.Precision
        agent.interest_on_deposits = max(0, agent.interest_on_deposits)
        assert agent in agent.deposits_bank.deposits_list