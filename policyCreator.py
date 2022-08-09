import glob
import pandas as pd
import numpy as np
import yaml
import random
import utils

# load config
with open('config.yaml') as stream:
        config = yaml.safe_load(stream)

windowSize = config['windowSize']
randomPolicyCreation = config['randomPolicyCreation']
randomNumberOfPolicyRules = config['randomNumberOfPolicyRules']
minNumberOfPolicyRules = config['minNumberOfPolicyRules']
maxNumberOfPolicyRules = config['maxNumberOfPolicyRules']
exactNumberOfPolicyRules = config['exactNumberOfPolicyRules']
completePolicyCreation = config['completePolicyCreation']
expertPolicyCreation = config['expertPolicyCreation']
aggregateFunctions = config['aggregateFunctions'] # avg, min, max

AGGREGATEFUNCTION = aggregateFunctions[0]
SEED = config['seed']
POLICYCOLUMNS = utils.POLICYCOLUMNS

# set seed
random.seed(SEED)
print(random.random())

def createPolicy():

    # load the csv with windowSize
    filenames = [file for file in glob.glob('./*.csv') if 'policy({}).csv'.format(windowSize) in file]
    csvPolicy = pd.read_csv(filenames[0], header = None)
    
    # postprocess: set header and group by malwaretype
    csvPolicy.columns = POLICYCOLUMNS
    #print(malwareGroup.get_group('httpbackdoor')) # DEBUG
    malwareGroup = csvPolicy.groupby(['malware'])
   
    # policy creation
    policy = pd.DataFrame()
    
    # random policy creation
    # iterate over all malware groups and add some (random or defined) rules (row) for each malware type
    if randomPolicyCreation == True:
        method = 'random'
        if randomNumberOfPolicyRules == True:
            method += '({}-{})'.format(minNumberOfPolicyRules, maxNumberOfPolicyRules)
        else:
            method += '({})'.format(exactNumberOfPolicyRules)

        for malware in malwareGroup:     
            # malware is a tuple: (name, df)
            rows = malware[1].shape[0] # number of rows for that malware type
            
            # random number of rules
            if randomNumberOfPolicyRules == True:
                
                # define random number between min/max number of policy rules
                random.seed(SEED)
                nRules = random.choice([minNumberOfPolicyRules, maxNumberOfPolicyRules])
                
            # defined number of rules
            else:
                nRules = exactNumberOfPolicyRules
            
            # make sure we don't have more rules than rows
            while(rows < nRules): 
                    nRules -= 1    
                
            
            #print(malware[1].sample(n = nRules)) # DEBGUG
            # add defined rules to policy
            policy = policy.append(malware[1].sample(n = nRules, random_state=SEED)) #todo check what happens if nRules > n when set
            policy = policy.drop_duplicates(subset=['metric'])
    
    # complete policy creation
    # iterate over all malware groups and all rules (row) for each malware type
    elif completePolicyCreation == True:
        method = 'complete'
        policy = csvPolicy
    
    # expert policy creation
    elif expertPolicyCreation == True:
        method = 'expert'
        pass
        # to be done
        

    # postprocessing
    policy['metric'] = policy['metric'].str.replace('-{}'.format(AGGREGATEFUNCTION), '') # remove aggregate function string for all rows
    policyName = 'policy({})-{}-{}'.format(windowSize, AGGREGATEFUNCTION, method)
    policy.to_csv('{}.csv'.format(policyName), index=False)
    
    return policy


def factors(policy):

    # classify each malware by type and add type column
    bd = ['httpbackdoor', 'BASHLITE', 'backdoor',  'jakoritarleite', 'The Tick']
    rk = ['beurk', 'bdvl']
    rw = ['Ransomware']
    conditions = [
        (policy['malware'].isin(bd)),
        (policy['malware'].isin(rk)),
        (policy['malware'].isin(rw))
    ]
    values = ['CnC', 'Rootkit', 'Ransomware']
    policy['malwaretype'] = np.select(conditions, values)
    
    # count different malware types and create a dict
    malwareTypes = policy['malwaretype'].value_counts().index.tolist()
    malwareOccurrences = policy['malwaretype'].value_counts().values.tolist()
    malwareTypeOcc = {malwareTypes[i]: malwareOccurrences[i] for i in range(len(malwareTypes))}
    
    # count total occurences of all malware types
    totalOccurences = sum(malwareOccurrences)
    return [malwareTypeOcc, totalOccurences, np.divide(malwareOccurrences, totalOccurences)]