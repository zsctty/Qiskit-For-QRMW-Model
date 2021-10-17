#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library import *

c4xgate = C4XGate()
c3xgate = C3XGate()


# In[2]:


def getEtraQubits(NumQubits):
    #get extra qubits for calculate
    extraqubit = 0
    while True:
        temp_quotient = int(NumQubits // 4)
        temp_remainder = int(NumQubits % 4)
        extraqubit += temp_quotient
        if temp_quotient + temp_remainder <= 4:
            return extraqubit+1
        NumQubits = temp_quotient + temp_remainder


# In[3]:


def getEquivalentDec(inputbitlength):
    # get equip decompose for ncnot gate
    
    index = inputbitlength 
    contorlArrayIndex = 0
    bitlength = inputbitlength - 1
    CNNotGateArray = []
    flag = bitlength
    while(bitlength >= 4):
        restLength = bitlength % 4
        implementLength = int(bitlength / 4)
        for i in range(implementLength):
            if flag == contorlArrayIndex*4:
                CNNotGateArray.append([4,
                                       contorlArrayIndex*4 + 1,
                                       contorlArrayIndex*4 + 2,
                                       contorlArrayIndex*4 + 3,
                                       contorlArrayIndex*4 + 4,
                                       index])
                contorlArrayIndex += 1
                index += 1
            elif flag == contorlArrayIndex*4 + 1:
                CNNotGateArray.append([4,
                                       contorlArrayIndex*4 ,
                                       contorlArrayIndex*4 + 2,
                                       contorlArrayIndex*4 + 3,
                                       contorlArrayIndex*4 + 4,
                                       index])
                contorlArrayIndex += 1
                index += 1
            elif flag == contorlArrayIndex*4 + 2:
                CNNotGateArray.append([4,
                                       contorlArrayIndex*4 ,
                                       contorlArrayIndex*4 + 1,
                                       contorlArrayIndex*4 + 3,
                                       contorlArrayIndex*4 + 4,
                                       index])
                contorlArrayIndex += 1
                index += 1
            elif flag == contorlArrayIndex*4 + 3:
                CNNotGateArray.append([4,
                                       contorlArrayIndex*4 ,
                                       contorlArrayIndex*4 + 1,
                                       contorlArrayIndex*4 + 2,
                                       contorlArrayIndex*4 + 4,
                                       index])
                contorlArrayIndex += 1
                index += 1
            else :
                CNNotGateArray.append([4,
                                       contorlArrayIndex*4,
                                       contorlArrayIndex*4 + 1,
                                       contorlArrayIndex*4 + 2,
                                       contorlArrayIndex*4 + 3,
                                       index])
                contorlArrayIndex += 1
                index += 1
        bitlength = restLength + implementLength
#     if bitlength == 1:
#         CNNotGateArray.append([1, index - 1, index])
    if bitlength == 2 :
        CNNotGateArray.append([2, inputbitlength - 2, index - 1, index])
    elif bitlength == 3 :
        CNNotGateArray.append([3, inputbitlength - 2, index - 2, index - 1, index])
    return CNNotGateArray


# In[4]:


getEquivalentDec(20)


# In[5]:


def getDecomposeArray(inputbitlength):
    # 对ncnot控制序列进行分解，以4cnot为基础门，通过使用额外存储量子比特进行分解
    index = inputbitlength
    contorlArrayIndex = 0
    bitlength = inputbitlength
    CNNotGateArray = []
    while(bitlength >= 4):
        restLength = bitlength % 4
        implementLength = int(bitlength / 4)
        for i in range(implementLength):
            CNNotGateArray.append([4,
                                   contorlArrayIndex*4,
                                   contorlArrayIndex*4 + 1,
                                   contorlArrayIndex*4 + 2,
                                   contorlArrayIndex*4 + 3,
                                   index])
            contorlArrayIndex += 1
            index += 1
        bitlength = restLength + implementLength
#     if bitlength == 1:
#         CNNotGateArray.append([1, index - 1, index])
    if bitlength == 2:
        CNNotGateArray.append([2, index - 2, index - 1, index])
    elif bitlength == 3:
        CNNotGateArray.append([3, index - 3, index - 2, index - 1, index])
    return CNNotGateArray


# In[6]:


def createOCControl(searchQbitArrLength, grover_circuit, initial_state = 0):
    #创建 grove 搜索的 Oracle 此处 Oracle 为5量子比特及以上搜索的序列，并对该序列进行实际的创建与分解
    #get gate decompose index array
    DecomposeArray = getDecomposeArray(searchQbitArrLength)
    DecomposeArrayLength = np.array(DecomposeArray).shape[0]
    #create oracle
    #forward apply gate to the quantum circuit
    searchControlIndex = 0
    for gate in DecomposeArray:
        if gate[0] == 4:
            grover_circuit.append(c4xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3]+ initial_state, 
                                            gate[4] + initial_state, gate[5] + initial_state])
            searchControlIndex = gate[5] + initial_state
        elif gate[0] == 1:
            grover_circuit.cx(gate[1] + initial_state, gate[2] + initial_state)
            searchControlIndex = gate[2] + initial_state
        elif gate[0] == 2:
            grover_circuit.ccx(gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state)
            searchControlIndex = gate[3] + initial_state
        elif gate[0] == 3:
            grover_circuit.append(c3xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state, 
                                            gate[4] + initial_state])
            searchControlIndex = gate[4] + initial_state
            
    grover_circuit.cx(searchControlIndex, searchControlIndex + 1)
    
    #backward revert quantum circuit
    for index in range(DecomposeArrayLength):
        gate = DecomposeArray[-1-index]
        if gate[0] == 4:
            grover_circuit.append(c4xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state, 
                                            gate[4] + initial_state, gate[5] + initial_state])
        elif gate[0] == 1:
            grover_circuit.cx(gate[1] + initial_state, gate[2] + initial_state)
        elif gate[0] == 2:
            grover_circuit.ccx(gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state)
        elif gate[0] == 3:
            grover_circuit.append(c3xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state, 
                                            gate[4] + initial_state])


# In[7]:


def createDifControl(searchQbitArrLength, grover_circuit, initial_state = 0):
     #创建 grove 搜索的 Diffuse 此处 Diffuse 为5量子比特及以上搜索的序列，并对该序列进行实际的创建与分解
    #get gate decompose index array
    DecomposeArray = getEquivalentDec(searchQbitArrLength)
    DecomposeArrayLength = np.array(DecomposeArray).shape[0]
    print(DecomposeArrayLength)
    #create oracle
    #forward apply gate to the quantum circuit
    searchControlIndex = 0
    for gate in DecomposeArray:
        if gate[0] == 4:
            grover_circuit.append(c4xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state, 
                                            gate[4] + initial_state, gate[5] + initial_state])
            searchControlIndex = gate[5] + initial_state
        elif gate[0] == 1:
            grover_circuit.cx(gate[1] + initial_state, gate[2] + initial_state)
            searchControlIndex = gate[2] + initial_state
        elif gate[0] == 2:
            grover_circuit.ccx(gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state)
            searchControlIndex = gate[3] + initial_state
        elif gate[0] == 3:
            grover_circuit.append(c3xgate, [gate[1] + initial_state, gate[2] + initial_state, 
                                            gate[3] + initial_state, gate[4] + initial_state])
            searchControlIndex = gate[4] + initial_state
    grover_circuit.barrier()        
    grover_circuit.cx(searchControlIndex, searchQbitArrLength - 1 + initial_state)
    grover_circuit.barrier()
    #backward revert quantum circuit
    for index in range(DecomposeArrayLength):
        gate = DecomposeArray[-1-index]
        if gate[0] == 4:
            grover_circuit.append(c4xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state, 
                                            gate[4] + initial_state, gate[5] + initial_state])
        #############################
        #in fact gate[0]=1 is useless
        ############################
        elif gate[0] == 1:
            grover_circuit.cx(gate[1] + initial_state, gate[2] + initial_state)
        elif gate[0] == 2:
            grover_circuit.ccx(gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state)
        elif gate[0] == 3:
            grover_circuit.append(c3xgate, [gate[1] + initial_state, gate[2] + initial_state, gate[3] + initial_state,
                                            gate[4] + initial_state])


# In[8]:


[i + 10 for i in range(10)]


# In[9]:


def createOracle(searchqbitarr, grover_circuit, initial_state = 0):
    #创建整体的grove搜索电路 包含oracle和diffuse两部分
    searchQbitArrIndex = list(searchqbitarr)

    searchQbitArrLength = np.array(searchQbitArrIndex).size
    
    #invert every 0 bits
    for i in range(searchQbitArrLength):
        if searchQbitArrIndex[i] == '0':
            grover_circuit.x(i + initial_state)
    grover_circuit.barrier()
    
    createOCControl(searchQbitArrLength, grover_circuit, initial_state)
    
    #invert every 0 bits
    for i in range(searchQbitArrLength):
        if searchQbitArrIndex[i] == '0':
            grover_circuit.x(i + initial_state)
            
    grover_circuit.barrier()
    
    #create diffuser(us)
    grover_circuit.h([i + initial_state for i in range(searchQbitArrLength)])
    grover_circuit.x([i + initial_state for i in range(searchQbitArrLength)])
    grover_circuit.barrier()
    grover_circuit.h(searchQbitArrLength - 1 + initial_state)   
    grover_circuit.barrier()
    createDifControl(searchQbitArrLength, grover_circuit, initial_state)
#     grover_circuit.append(c4xgate, [0, 1, 2, 3, 4])
    grover_circuit.barrier()
    grover_circuit.h(searchQbitArrLength - 1 + initial_state)
    grover_circuit.barrier()
    grover_circuit.x([i + initial_state for i in range(searchQbitArrLength)])
    grover_circuit.h([i + initial_state for i in range(searchQbitArrLength)])


# In[10]:


def createCOlorCCon(placeIndexLength, quantumcircuit, colorInf):
    #get gate decompose index array
    DecomposeArray = getDecomposeArray(placeIndexLength)
    DecomposeArrayLength = np.array(DecomposeArray).shape[0]
    #create oracle
    #forward apply gate to the quantum circuit
    if colorInf == 1:
        colorControlIndex = 0
        for gate in DecomposeArray:
            if gate[0] == 4:
                quantumcircuit.append(c4xgate, [gate[1], gate[2], gate[3], gate[4], gate[5]])
                colorControlIndex = gate[5]
            elif gate[0] == 1:
                quantumcircuit.cx(gate[1], gate[2])
                colorControlIndex = gate[2]
            elif gate[0] == 2:
                quantumcircuit.ccx(gate[1], gate[2], gate[3])
                colorControlIndex = gate[3]
            elif gate[0] == 3:
                quantumcircuit.append(c3xgate, [gate[1], gate[2], gate[3], gate[4]])
                colorControlIndex = gate[4]

        quantumcircuit.cx(colorControlIndex, colorControlIndex + 1)

        #backward revert quantum circuit
        for index in range(DecomposeArrayLength):
            gate = DecomposeArray[-1-index]
            if gate[0] == 4:
                quantumcircuit.append(c4xgate, [gate[1], gate[2], gate[3], gate[4], gate[5]])
            elif gate[0] == 1:
                quantumcircuit.cx(gate[1], gate[2])
            elif gate[0] == 2:
                quantumcircuit.ccx(gate[1], gate[2], gate[3])
            elif gate[0] == 3:
                quantumcircuit.append(c3xgate, [gate[1], gate[2], gate[3], gate[4]])
    else :
        if int(colorInf, 2) != 0:
            colorControlIndex = 0
            colorInfLength = np.array(list(colorInf)).size
            for gate in DecomposeArray:
                if gate[0] == 4:
                    quantumcircuit.append(c4xgate, [gate[1], gate[2], gate[3], gate[4], gate[5]])
                    colorControlIndex = gate[5]
                elif gate[0] == 1:
                    quantumcircuit.cx(gate[1], gate[2])
                    colorControlIndex = gate[2]
                elif gate[0] == 2:
                    quantumcircuit.ccx(gate[1], gate[2], gate[3])
                    colorControlIndex = gate[3]
                elif gate[0] == 3:
                    quantumcircuit.append(c3xgate, [gate[1], gate[2], gate[3], gate[4]])
                    colorControlIndex = gate[4]

            for index in range(colorInfLength):
                if colorInf[index] == '1':
                    quantumcircuit.cx(colorControlIndex, colorControlIndex + 1 + index)

            #backward revert quantum circuit
            for index in range(DecomposeArrayLength):
                gate = DecomposeArray[-1-index]
                if gate[0] == 4:
                    quantumcircuit.append(c4xgate, [gate[1], gate[2], gate[3], gate[4], gate[5]])
                elif gate[0] == 1:
                    quantumcircuit.cx(gate[1], gate[2])
                elif gate[0] == 2:
                    quantumcircuit.ccx(gate[1], gate[2], gate[3])
                elif gate[0] == 3:
                    quantumcircuit.append(c3xgate, [gate[1], gate[2], gate[3], gate[4]])
        


# In[11]:


def createTwoValQImage(placeIndex, colorInf, quantumcircuit):
    placeIndex = list(placeIndex)
#     print(placeIndex)
    placeIndexLength = np.array(placeIndex).size
#     print(placeIndexLength)
    
    if colorInf == 0:
        return 
    
    #invert every 0 bits
    for i in range(placeIndexLength):
        if placeIndex[i] == '0':
            quantumcircuit.x(i)
    quantumcircuit.barrier()
    
    
    createCOlorCCon(placeIndexLength, quantumcircuit, colorInf)

    #revert every 0 bits
    for i in range(placeIndexLength):
        if placeIndex[i] == '0':
            quantumcircuit.x(i)
    quantumcircuit.barrier()


# In[12]:


def createGrayQImage(placeIndex, colorInf, quantumcircuit):
    placeIndex = list(placeIndex)
#     print(placeIndex)
    placeIndexLength = np.array(placeIndex).size
#     print(placeIndexLength)
    
    if colorInf == '00000000':
        return 
    
    #invert every 0 bits
    for i in range(placeIndexLength):
        if placeIndex[i] == '0':
            quantumcircuit.x(i)
    quantumcircuit.barrier()
    
    #get gate decompose index array
    DecomposeArray = getDecomposeArray(placeIndexLength)
    DecomposeArrayLength = np.array(DecomposeArray).size
    
    createCOlorCCon(placeIndexLength, quantumcircuit, colorInf)
    
    #revert every 0 bits
    for i in range(placeIndexLength):
        if placeIndex[i] == '0':
            quantumcircuit.x(i)
    quantumcircuit.barrier()


# In[13]:


import math
def getGroveIterNum(searchArrLength):
    Pi = math.pi
    N = math.pow(2, searchArrLength)
    iterNum = int(Pi/4*math.sqrt(N))
    return iterNum


# In[ ]:




