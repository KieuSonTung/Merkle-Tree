# Check whether a list is a sub list of another list
# Run python checkconsistency.py --lista value1 value2 value3 --listb value1 value2 value3 value4 ...

import hashlib, sys, argparse
from buildmtree import *


def getHashValue(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def combined(value1, value2):
    combinedValue = value1 + value2
    return combinedValue


def checkConsistency(leaves1, leaves2):
    i = 0
    while i < len(leaves1):
        if leaves1[i] != leaves2[i]:
            break
        i += 1
    if i < len(leaves1):
        return []
    f = open("merkle.trees", "w")
    f.write("Merkle Tree 1 \n")
    root1 = buildTree(leaves1, f)
    f.write("\n\n")
    f.write("Merkle Tree 2 \n")
    root2 = buildTree(leaves2, f)
    f.close()

    with open("merkle.trees") as f:
        data = f.readlines()

    tree2Index = 0
    for i in range(len(data)):
        if data[i].startswith("Merkle Tree 2"):
            tree2Index = i
    parentLines = []
    leftChildLines = []
    rightChildLines = []

    for i in range(tree2Index, len(data)):
        if data[i].startswith("Parent("):
            parentLines.append(data[i])

    for i in range(tree2Index, len(data)):
        if data[i].startswith("Left"):
            leftChildLines.append(data[i])

    for i in range(tree2Index, len(data)):
        if data[i].startswith("Right"):
            rightChildLines.append(data[i])
    op = []
    flag = False
    for i in range(len(parentLines)):
        if root1.hashValue in parentLines[i]:
            flag = True
            break
    if flag:
        values = []
        combinedHash = ''
        lc = root1.value
        while combinedHash != root2.hashValue:
            for i in range(len(leftChildLines)):
                if lc in leftChildLines[i].split(" ")[-6]:
                    rc = rightChildLines[i].split(" ")[-6]
                    values.append(getHashValue(rc))
                    break
            combinedValue = combined(getHashValue(lc), getHashValue(rc))
            combinedHash = getHashValue(combinedValue)
            lc = combinedValue

        op.append(root1.hashValue)
        op += values
        op.append(root2.hashValue)

    else:
        root1LeftChildValue = data[tree2Index - 5].split(" ")[-6]
        root1RightChildValue = data[tree2Index - 4].split(" ")[-6]
        root1RightChildSiblingValue = leaves2[leaves2.index(root1RightChildValue) + 1]
        values = [getHashValue(root1LeftChildValue), getHashValue(root1RightChildValue),
                  getHashValue(root1RightChildSiblingValue)]
        root1RightChildCombinedValue = combined(getHashValue(root1RightChildValue),
                                                getHashValue(root1RightChildSiblingValue))
        combinedHash = ''
        lc = root1LeftChildValue
        rc = root1RightChildCombinedValue
        while combinedHash != root2.hashValue:
            combinedValue = combined(getHashValue(lc), getHashValue(rc))
            combinedHash = getHashValue(combinedValue)
            lc = combinedValue
            for i in range(len(leftChildLines)):
                if lc in leftChildLines[i].split(" ")[-6]:
                    rc = rightChildLines[i].split(" ")[-6]
                    values.append(getHashValue(rc))
                    break

        op.append(root1.hashValue)
        op += values
        op.append(root2.hashValue)

    return op


CLI = argparse.ArgumentParser()
CLI.add_argument(
  "--lista",  # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",  # 0 or more values expected => creates a list
  type=str,
  default=[],  # default if nothing is provided
)
CLI.add_argument(
  "--listb",
  nargs="*",
  type=str,  # any type/callable can be used here
  default=[],
)

# parse the command line
args = CLI.parse_args()

leaves1 = args.lista
leaves2 = args.listb

op = checkConsistency(leaves1, leaves2)
if len(op) > 0:
    print("Yes", op)
else:
    print("No")
