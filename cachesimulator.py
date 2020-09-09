# File: cachesimulator.py
# Author: Ryan Mendoza
# Date: 5/4/2020
# Section: 511
# E-mail: ryanmen1102@tamu.edu
# Description:
# Cache Simulator

import sys
import math
import random

if len(sys.argv) != 2:
    print("Please enter a file name")
    sys.exit()

memSize = 0

with open(sys.argv[1], "r") as inFile:
    ram = {}
    address = 0
    for line in inFile:
        hexNum = "0x"
        hexNum += hex(address)[2:].zfill(2).upper()
        ram[hexNum] = line[:2]
        address += 1
        memSize += 1
        # print(str + ": " + ram[str])
    print("*** Welcome to the cache simulator ***" + '\n' + 
          "initialize the RAM:" + '\n' +
          "init-ram 0x00 0xFF" + '\n' +
          "ram successfully initialized!")

print("configure the cache:")
# print("cache size: ")
cacheSize = int(input("cache size: "))
blockSize = int(input("data block size: "))
assoc = int(input("associativity: "))
replacePolicy = int(input("replacement policy: "))
hitPolicy = int(input("write hit policy: "))
missPolicy = int(input("write miss policy: "))
print("cache successfully configured!")

blockBits = int(math.log(blockSize, 2))
setTotal = int(cacheSize / (assoc * blockSize))
setBits = int(math.log(setTotal, 2))
addBits = 8
tagBits = int(addBits - (blockBits + setBits))
linePerSet = assoc
hitCount = 0
missCount = 0
random.seed()

cache = []
for i in range(0, setTotal): # make setTotal sublists
    cache.append([])
    for j in range(0, assoc): # make assoc sublists (lines) in each set
        cache[i].append([])
        for k in range(0, blockSize + 4): # make blockSize+4 sublists in each line
            if (k >= 3): # tag and block data set to 00
                cache[i][j].append("00")
            else:
                cache[i][j].append(0)

# cache[set][line][block+4] to refer to block data
# cache[set][line][0] is valid bit for that line
# cache[set][line][1] is dirty bit for that line
# cache[set][line][2] is data for LRU and LFU replacement
# cache[set][line][3] is the tag for that line
# everything starts off as a single 0

while(True):
    bruh = input("*** Cache simulator menu ***" + '\n' +
        "type one command:" + '\n' +
        "1. cache-read" + '\n' +
        "2. cache-write" + '\n' +
        "3. cache-flush" + '\n' +
        "4. cache-view" + '\n' +
        "5. memory-view" + '\n' +
        "6. cache-dump" + '\n' +
        "7. memory-dump" + '\n' +
        "8. quit" + '\n' +
        "****************************" + '\n')
    words = bruh.split()
    if (words[0] == "quit"):
        break
    elif (words[0] == "cache-read"):
        bitAddress = bin(int(words[1][2:], 16))[2:].zfill(8)
        try:
            tagNum = hex(int(bitAddress[:tagBits], 2))[2:].zfill(2).upper()
        except:
            tagNum = "00"
        try:
            setNum = int(bitAddress[tagBits:tagBits+setBits], 2)
        except:
            setNum = 0
        try:
            blockNum = int(bitAddress[tagBits+setBits:], 2)
        except:
            blockNum = 0
        decStartOfLine = int(words[1][2:], 16) - blockNum
        
        lowest = 0
        highest = 0
        hit = False
        readComplete = False
        data = ram["0x" + words[1][2:].upper()]
        evictLine = -1
        ramAddress = "0x" + words[1][2:].upper()
        
        # find lowest and highest LRU value (lowest is replaced and highest + 1 is next value)
        lowest = cache[setNum][0][2] # set to the first line's LRU data
        highest = cache[setNum][0][2]
        for line in cache[setNum]:
            lowest = min(lowest, line[2])
            highest = max(highest, line[2])
            
        for line in cache[setNum]: # check each line in set for tag and valid bit for a cache hit
            if (line[3] == tagNum and line[0] == 1):
                data = line[blockNum+4]
                hit = True
                if (replacePolicy == 3):
                    line[2] += 1
                else:
                    line[2] = highest + 1
                hitCount += 1
                evictLine = -1
                ramAddress = "-1"
                
        if (hit == False): # for a cache miss 
            missCount += 1
            for line in cache[setNum]: # check for invalid to replace
                evictLine += 1
                if (line[0] == 0 and readComplete == False):
                    line[0] = 1
                    if (replacePolicy == 3):
                        line[2] += 1
                    else:
                        line[2] = highest + 1
                    line[3] = tagNum
                    for i in range(4, 4+blockSize):
                        line[i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                    readComplete = True
                    data = line[blockNum+4]
                    break
                    
            if (readComplete == False and (replacePolicy == 2 or replacePolicy == 3)): # if no invalid to replace, then find lowest LRU to replace
                evictLine = -1
                for line in cache[setNum]:
                    evictLine += 1
                    if (line[2] == lowest):
                        line[0] = 1
                        if (replacePolicy == 3):
                            line[2] += 1
                        else:
                            line[2] = highest + 1
                        line[3] = tagNum
                        for i in range(4, 4+blockSize):
                            line[i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                        readComplete = True
                        data = line[blockNum+4]
                        break
                        
            if (readComplete == False and replacePolicy == 1): # if no invalid, random replacement
                evictLine = random.randint(0, linePerSet-1)
                cache[setNum][evictLine][0] = 1
                cache[setNum][evictLine][2] = highest + 1
                cache[setNum][evictLine][3] = tagNum
                for i in range(4, 4+blockSize):
                    cache[setNum][evictLine][i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                readComplete = True
                data = cache[setNum][evictLine][blockNum+4]
                
        print("set:" + str(setNum))
        print("tag:" + (str(tagNum).upper() if tagNum[0] != "0" else str(tagNum).upper()[1]))
        print("hit:" + ("yes" if hit == True else "no"))
        print("eviction_line:" + str(evictLine))
        print("ram address:" + ramAddress)
        print("data:" + data)
    elif (words[0] == "cache-write"):
        bitAddress = bin(int(words[1][2:], 16))[2:].zfill(8)
        try:
            tagNum = hex(int(bitAddress[:tagBits], 2))[2:].zfill(2).upper()
        except:
            tagNum = "00"
        try:
            setNum = int(bitAddress[tagBits:tagBits+setBits], 2)
        except:
            setNum = 0
        try:
            blockNum = int(bitAddress[tagBits+setBits:], 2)
        except:
            blockNum = 0
        decStartOfLine = int(words[1][2:], 16) - blockNum
        
        lowest = 0
        highest = 0
        hit = False
        readComplete = False
        data = words[2][2:].upper()
        evictLine = -1
        ramAddress = "0x" + words[1][2:].upper()
        dirtyBit = 0
        
        # find lowest and highest LRU value (lowest is replaced and highest + 1 is next value)
        lowest = cache[setNum][0][2] # set to the first line's LRU data
        highest = cache[setNum][0][2]
        for line in cache[setNum]:
            lowest = min(lowest, line[2])
            highest = max(highest, line[2])
            
        for line in cache[setNum]: # check each line in set for tag and valid bit for a cache hit
            if (line[3] == tagNum and line[0] == 1):
                line[blockNum+4] = data
                hit = True
                if (replacePolicy == 3):
                    line[2] += 1
                else:
                    line[2] = highest + 1
                hitCount += 1
                evictLine = -1
                ramAddress = "-1"
                if (hitPolicy == 1):
                    ram[ramAddress] = data
                elif (hitPolicy == 2):
                    line[1] = 1
                    dirtyBit = 1
                
        if (hit == False and missPolicy == 1): # for a cache miss and write-allocate
            missCount += 1
            for line in cache[setNum]: # check for invalid to replace
                evictLine += 1
                if (line[0] == 0 and readComplete == False):
                    line[0] = 1
                    if (replacePolicy == 3):
                        line[2] += 1
                    else:
                        line[2] = highest + 1
                    line[3] = tagNum
                    for i in range(4, 4+blockSize):
                        line[i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                    readComplete = True
                    line[blockNum+4] = data
                    if (hitPolicy == 1):
                        ram[ramAddress] = data
                    elif (hitPolicy == 2):
                        line[1] = 1
                        dirtyBit = 1
                    break
                    
            if (readComplete == False and (replacePolicy == 2 or replacePolicy == 3)): # if no invalid to replace, then find lowest LRU to replace
                evictLine = -1
                for line in cache[setNum]:
                    evictLine += 1
                    if (line[2] == lowest):
                        line[0] = 1
                        if (replacePolicy == 3):
                            line[2] += 1
                        else:
                            line[2] = highest + 1
                        line[3] = tagNum
                        for i in range(4, 4+blockSize):
                            line[i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                        readComplete = True
                        line[blockNum+4] = data
                        if (hitPolicy == 1):
                            ram[ramAddress] = data
                        elif (hitPolicy == 2):
                            line[1] = 1
                            dirtyBit = 1
                        break
                        
            if (readComplete == False and replacePolicy == 1): # if no invalid, random replacement
                evictLine = random.randint(0, linePerSet-1)
                cache[setNum][evictLine][0] = 1
                cache[setNum][evictLine][2] = highest + 1
                cache[setNum][evictLine][3] = tagNum
                for i in range(4, 4+blockSize):
                    cache[setNum][evictLine][i] = ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()]
                readComplete = True
                cache[setNum][evictLine][blockNum+4] = data
                if (hitPolicy == 1):
                    ram[ramAddress] = data
                elif (hitPolicy == 2):
                    cache[setNum][evictLine][1] = 1
                    dirtyBit = 1
                    
        elif (hit == False and missPolicy == 2):
            missCount += 1
            ram[ramAddress] = data
                
        print("set:" + str(setNum))
        print("tag:" + (str(tagNum).upper() if tagNum[0] != "0" else str(tagNum).upper()[1]))
        print("write_hit:" + ("yes" if hit == True else "no"))
        print("eviction_line:" + str(evictLine))
        print("ram address:" + ramAddress)
        print("data:" + "0x" + data)
        print("dirty_bit:" + str(dirtyBit))
    elif (words[0] == "cache-flush"):
        setNum = -1
        for set in cache:
            setNum += 1
            for line in set:
                if (line[1] == 1):
                    if (tagBits == 0):
                        bitAddress = bin(setNum)[2:].zfill(setBits)
                    elif (setBits == 0):
                        bitAddress = bin(int(line[3], 16))[2:].zfill(tagBits)
                    else:
                        bitAddress = bin(int(line[3], 16))[2:].zfill(tagBits) + bin(setNum)[2:].zfill(setBits)
                    
                    decStartOfLine = int(bitAddress.ljust(8, "0"), 2)
                    print(bitAddress)
                    print(decStartOfLine)
                    for i in range(4, 4+blockSize):
                        ram["0x" + hex(decStartOfLine + (i-4))[2:].zfill(2).upper()] = line[i]
                for i in range(0, blockSize+4):
                    if (i >= 3):
                        line[i] = "00"
                    else:
                        line[i] = 0
        print("cache_cleared")
    elif (words[0] == "cache-view"):
        if (replacePolicy == 1):
            wordReplace = "random_replacement"
        elif (replacePolicy == 2):
            wordReplace = "least_recently_used"
        elif (replacePolicy == 3):
            wordReplace = "least_frequently_used"
        
        if (hitPolicy == 1):
            wordHit = "write_through"
        else:
            wordHit = "write_back"
        
        if (missPolicy == 1):
            wordMiss = "write_allocate"
        else:
            wordMiss = "no_write_allocate"
        
        print("cache_size:" + str(cacheSize))
        print("data_block_size:" + str(blockSize))
        print("associativity:" + str(assoc))
        print("replacement_policy:" + wordReplace)
        print("write_hit_policy:" + wordHit)
        print("write_miss_policy:" + wordMiss)
        print("number_of_cache_hits:" + str(hitCount))
        print("number_of_cache_misses:" + str(missCount))
        print("cache_content:")
        for set in cache:
            for line in set:
                lineInfo = ""
                for i in range(0, blockSize+4):
                    if (i == 2):
                        continue
                    elif (i == blockSize+3):
                        lineInfo += str(line[i])
                    else:
                        lineInfo += (str(line[i]) + " ")
                print(lineInfo)
    elif (words[0] == "memory-view"):
        print("memory_size:" + str(memSize))
        print("memory_content:")
        print("Address:Data")
        
        addressNum = 0
        while (addressNum < memSize):
            hexNum = "0x" + hex(addressNum)[2:].zfill(2).upper()
            lineData = ""
            for i in range(0, 8):
                if (i == 7):
                    lineData += ram["0x" + hex(addressNum + i)[2:].zfill(2).upper()]
                else:
                    lineData += (ram["0x" + hex(addressNum + i)[2:].zfill(2).upper()] + " ")
            print(hexNum + ":" + lineData)
            addressNum += 8
        
    elif (words[0] == "cache-dump"):
        with open("cache.txt", "w") as outFile:
            for set in cache:
                for line in set:
                    lineInfo = ""
                    for i in range(4, blockSize+4):
                        if (i == blockSize + 3):
                            lineInfo += str(line[i])
                        else:
                            lineInfo += (str(line[i]) + " ")
                    outFile.write(lineInfo + '\n')
    elif (words[0] == "memory-dump"):
        with open("ram.txt", "w") as outFile:
            addressNum = 0
            while (addressNum < memSize-1):
                hexNum = "0x" + hex(addressNum)[2:].zfill(2).upper()
                outFile.write(ram[hexNum] + '\n')
                addressNum += 1
            hexNum = "0x" + hex(addressNum)[2:].zfill(2).upper()
            outFile.write(ram[hexNum])
    