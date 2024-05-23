import sys
import re

def wordsReplace(text, s,r):
    return re.sub(re.escape(s) + '(?=[\=\(\)\$\[\]\{\}\+\-\*\/\:\;\&\!\<\>.,\s]|$)', r, text)

n = len(sys.argv)
if n == 1:
    print("BTrend - c64 basic sequence generator")
    print("")
    print("Usage")
    print("")
    print("btrend -in=<input> -out=<output> [options] ")
    print("")
    print("options:")
    print("  -v : verbose")
    print("  -s : skip comments")
    print("  -step=<num> : sequence step")
    print("  -t : turn on test mode")
    print("  -p : turn on pack mode")
    print("        pack mode: the marked rows will be grouped in one row")
    print("")
    print("e.g.: ")
    print("  python btrend.py \"-in=c:\\your folder\\input-file.txt\" \"-out=c:\\your folder\\output-file.txt\" -v -s -step=100")
    sys.exit(0)
inFile=None
outFile=None
verb=False
skipCm=False
seqStep=10
errs=False
testCase=False
packMode=False
defines1=[]
defines2=[]
vars1=[]
vars2=[]
methods=[]
methodVars=[]
for p in range(n):
    if p > 0:
        if sys.argv[p] == "-v":
            verb=True
        elif sys.argv[p] == "-s":
            skipCm=True
        elif len(sys.argv[p]) > 4 and (sys.argv[p])[:4] == "-in=":
            inFile=(sys.argv[p])[4:]
        elif len(sys.argv[p]) > 5 and (sys.argv[p])[:5] == "-out=":
            outFile=(sys.argv[p])[5:]
        elif len(sys.argv[p]) > 5 and (sys.argv[p])[:6] == "-step=":
            seqStep=int((sys.argv[p])[6:])
        elif sys.argv[p] == "-t":
            testCase=True
        elif sys.argv[p] == "-p":
            packMode=True
if inFile==None or outFile==None:
    print("Error: No input/output file specified")
    sys.exit(1)
if verb:
    print("Arguments:")
    print("  input file: " + inFile)
    print("  output file: " + outFile)
    print("  skip comments: " + str(skipCm))
    print("  sequence step: " + str(seqStep))
    if not testCase:
        print("  test cases: No")
    else:
        print("  test cases: Yes")

if verb:
    print("Reading content from input file...")
with open(inFile) as f:
    inLines2 = f.readlines()

t=0
while t<len(inLines2):
    if inLines2[t].strip()[:6]=="using ":
        usingPath = "./" + inLines2[t].split("\"")[1]
        if verb:
            print("Inserting file: " + usingPath)
        inLines2[t]=""
        with open(usingPath) as f:
            using=f.readlines()
        tmp=using+inLines2
        inLines2=tmp
    elif inLines2[t].strip()[:8]=="include ":
        usingPath = "./" + inLines2[t].split("\"")[1]
        if verb:
            print("Including file: " + usingPath)
        inLines2[t]=""
        with open(usingPath) as f:
            using=f.readlines()
        for x in range(len(using)):
            y=len(using)-(x+1)
            inLines2.insert(t,using[y])
    elif inLines2[t].strip()[:2]=="! ":
        if verb:
            print("Row is disabled with test mode: " + inLines2[t].strip())
        if not testCase:
            inLines2[t]="\t"+inLines2[t].strip()[2:]
        else:
            inLines2[t]=""
    elif inLines2[t].strip()[:2]=="? ":
        if verb:
            print("Row is enabled with test mode: " + inLines2[t].strip())
        if not testCase:
            inLines2[t]=""
        else:
            inLines2[t]="\t"+inLines2[t].strip()[2:]
    t=t+1

if packMode:
    t=0
    while t<len(inLines2):
        if inLines2[t].strip()=="[]":
            inLines2[t]=""
            q=t+2
            w=t+1
            cnt=0
            inLines2[w]=inLines2[w].rstrip()
            while inLines2[q].strip()!="[/]" and cnt<20:
                inLines2[w]=inLines2[w]+" :" + inLines2[q].strip()
                inLines2[q]=""
                q=q+1
                cnt=cnt+1
            if inLines2[q].strip()=="[/]":
                inLines2[q]=""
        elif inLines2[t].strip()=="[/]":
            inLines2[t]=""
        t=t+1
else:
    for t in range(len(inLines2)):
        z=inLines2[t].strip()
        if z=="[]" or z=="[/]":
            inLines2[t]=""

skipSubRoutine=10000
subRes=True
t=0
while t<len(inLines2):
    if inLines2[t].rstrip()[:7]=="struct ":
        sp=inLines2[t].rstrip().split()
        cName=sp[1]
        cBufSize=int(sp[2])
        if verb:
            print("Create '"+cName+"' struct & subroutines")
        q=t+1
        inLines2[t]=""
        elements=[]
        types=[]
        arrays=[]
        defaults=[]
        while q<len(inLines2) and inLines2[q].rstrip()[:3]!="---":
            sp=inLines2[q].rstrip().split()
            elements.append(sp[0])
            defaults.append(sp[1])
            if sp[1].startswith("\""):
                types.append("string")
                arrays.append(0)
            elif sp[1].startswith("ref"):
                types.append("ref")
                arrays.append(0)
            elif sp[1].startswith("("):
                types.append("array")
                arrNum=int(sp[1].replace("(","").replace(")",""))
                arrays.append(arrNum)
            else:
                types.append("number")
                arrays.append(0)
            inLines2[q]=""
            q=q+1
        if inLines2[q].rstrip()[:3]=="---":
            inLines2[q]=""
        ins=[]
        if subRes:
            ins.append("number SubResult")
            subRes=False
        ins.append("define "+cName+".MAX$="+str(cBufSize))
        ins.append("number "+cName+".$")
        for q in range(len(elements)):
            if (types[q]!="array"):
                ins.append(types[q]+" "+cName+"."+elements[q])
            else:
                ins.append("number "+cName+"."+elements[q])
        ins.append("\tDIM "+cName+".$("+str(cBufSize)+")")
        for q in range(len(elements)):
            if (types[q]!="array"):
                ins.append("\tDIM "+cName+"."+elements[q]+"("+str(cBufSize)+")")
            else:
                ins.append("\tDIM "+cName+"."+elements[q]+"("+str(cBufSize)+","+str(arrays[q])+")")
        ins.append("\tGOTO @skipSubRoutine"+str(skipSubRoutine)+":")
        ins.append("@New"+cName+":")
        ins.append("\tFOR SubResult=0 TO "+cName+".MAX$-1")
        ins.append("\tIF "+cName+".$(SubResult)<>1 THEN GOTO @new"+cName+":")
        ins.append("\tNEXT")
        ins.append("\tSubResult=-1")
        ins.append("\tRETURN")
        ins.append("@new"+cName+":")
        ins.append("\t"+cName+".$(SubResult)=1")
        for q in range(len(elements)):
            if (types[q]!="array"):
                ins.append("\t"+cName+"."+elements[q]+"(SubResult)="+defaults[q])
            else:
                ins.append("\tFORZ9=0TO"+str(arrays[q])+"-1:"+cName+"."+elements[q]+"(SubResult,Z9)=0:NEXT")
        ins.append("\tRETURN")

        ins.append("@Free"+cName+":")
        ins.append("\t"+cName+".$(SubResult)=0")
        for q in range(len(elements)):
            if types[q]=="string":
                ins.append("\t"+cName+"."+elements[q]+"(SubResult)=\"\"")
            else:
                ins.append("\t"+cName+"."+elements[q]+"(SubResult)=-1")
        ins.append("\tRETURN")

        ins.append("@skipSubRoutine"+str(skipSubRoutine)+":")
        skipSubRoutine=skipSubRoutine+1
        for x in range(len(ins)):
            y=len(ins)-(x+1)
            inLines2.insert(t,ins[y]+"\n")
        t=t+len(ins)
    elif inLines2[t].lstrip()[:4]=="NEW ":
        sp=inLines2[t].strip().split()
        cName=sp[1]
        if sp[2]=="AS":
            ref=sp[3]
            if verb:
                print("Found a new instance request with '"+ref+"'")
            inLines2[t]="\tGOSUB @New"+cName+": : "+ref+"=SubResult"
    elif inLines2[t].lstrip()[:5]=="FREE ":
        sp=inLines2[t].strip().split()
        cName=sp[1]
        ref=sp[2]
        if verb:
            print("Found a new instance request with '"+ref+"'")
        inLines2[t]="\tSubResult="+ref+":GOSUB @Free"+cName+":"
    
    elif inLines2[t].lstrip()[:5]=="enum ":
        sp=inLines2[t].strip().split()
        enumName=sp[1]
        if len(sp)>3:
            for x in range(len(sp)-3):
                sp[2]=sp[2]+sp[x+3].strip()
                sp[x+3]=""
        enums=sp[2].split(",")
        for x in range(len(enums)):
            defines1.append(enumName+"."+enums[x])
            defines2.append(str(x+1))
        inLines2[t]=""
    t = t + 1

withFinds=[]
withReplaces=[]
for x in range(len(inLines2)):
    if inLines2[x].lstrip()[:5]=="WITH ":
        sp=inLines2[x].strip().split()
        withFinds.append(sp[1]+".")
        withReplaces.append(sp[2]+".")
        inLines2[x]=""
    elif inLines2[x].strip()[:7]=="CLRWITH":
        withFinds=[]
        withReplaces=[]
        inLines2[x]=""
    if len(withFinds)>0:
        for y in range(len(withFinds)):
            if inLines2[x].find(withFinds[y]) > -1:
                inLines2[x]=inLines2[x].replace(withFinds[y],withReplaces[y])

withFinds=None
withReplaces=None

for t in range(len(inLines2)):

    if inLines2[t].find("'")>-1:
        row=inLines2[t].strip()
        for q in range(len(row)):
            finds=[]
            repls=[]
            if row[q]=="'":
                if row[q-1]=="h":
                    num=int("0x"+row[q+1:q+3], 0)
                    finds.append("h'"+row[q+1:q+3])
                    repls.append(str(num))
                elif row[q-1]=="H":
                    num=int("0x"+row[q+1:q+5], 0)
                    finds.append("H'"+row[q+1:q+5])
                    repls.append(str(num))
                elif row[q-1]=="B":
                    num=int(row[q+1:q+9], 2)
                    finds.append("B'"+row[q+1:q+9])
                    repls.append(str(num))
                elif row[q-1]=="b":
                    num=int(row[q+1:q+5], 2)
                    finds.append("b'"+row[q+1:q+5])
                    repls.append(str(num))
            for p in range(len(finds)):
                if verb:
                    print("Replace constant " + finds[p]+"  ->  "+repls[p])
                inLines2[t]=inLines2[t].replace(finds[p],repls[p])

    if inLines2[t].strip()[:7]=="define ":
        tmp=inLines2[t].strip()[7:].split("=")
        defines1.append(tmp[0].strip().replace("\\20"," "))
        defines2.append(tmp[1].strip().replace("\\20"," "))
        inLines2[t]=""

varIndex1=0
varIndex2=0
var1st="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
var2nd="0123456789"+var1st
for t in range(len(inLines2)):
    if inLines2[t].strip()[:7]=="number " or inLines2[t].strip()[:7]=="string ":
        varName=inLines2[t].strip()[7:]
        varRealName=var1st[varIndex1]+var2nd[varIndex2]
        if inLines2[t].strip()[:7]=="string ":
            varRealName=varRealName+"$"
        if verb:
            print("Create a variable to '"+varName+"' ('"+varRealName+"').")
        vars1.append(varName)
        vars2.append(varRealName)
        varIndex2 = varIndex2 + 1
        if varIndex2==len(var2nd):
            varIndex1 = varIndex1 + 1
            varIndex2 = 0
        inLines2[t]=""
    elif inLines2[t].strip()[:4]=="ref ":
        varName=inLines2[t].strip()[4:]
        varRealName=var1st[varIndex1]+var2nd[varIndex2]
        if verb:
            print("Create a reference to '"+varName+"' ('"+varRealName+"').")
        vars1.append(varName)
        vars2.append(varRealName)
        varIndex2 = varIndex2 + 1
        if varIndex2==len(var2nd):
            varIndex1 = varIndex1 + 1
            varIndex2 = 0
        inLines2[t]=""
    elif inLines2[t].strip()[:7]=="METHOD ":
        if verb:
            print("Add method: " + inLines2[t].strip())
        sp=inLines2[t].strip().split()
        methName=sp[1]
        if len(sp)>2:
            if len(sp)>3:
                for q in range(len(sp)-3):
                    sp[2]=sp[2]+sp[q+3]
            methPars=sp[2].split(",")
        else:
            methPars=[]
        inLines2[t]="@"+sp[1]+":"
        methods.append(methName)
        methodVars.append(methPars)
    elif inLines2[t].strip()[:5]=="CALL ":
        sp=inLines2[t].strip().split()
        methName=sp[1]
        if len(sp)>2:
            if len(sp)>3:
                for q in range(len(sp)-3):
                    sp[2]=sp[2]+sp[q+3]
            methValues=sp[2].split(",")
        else:
            methValues=[]
        methIndex=-1
        tmp=""
        for x in range(len(methods)):
            if methods[x]==methName:
                methIndex=x
                if len(methodVars[x])!=len(methValues):
                    print("Error: Call parameters is incorrect in " + inLines2[t].strip())
                    print("Method parameters: " + str(len(methodVars[x])))
                    print("Call parameters: " + str(len(methValues)))
                    sys.exit(1)
                for y in range(len(methodVars[x])):
                    parVal=methValues[y].replace(";",",")
                    tmp=tmp+methodVars[x][y]+"="+parVal+" : "
                tmp=tmp+"GOSUB @" + methName + ":"
                inLines2[t]=tmp

for t in range(len(defines1)):
    if verb:
        print("Replace defines, '"+defines1[t]+"' to '"+defines2[t]+"'.")
    for q in range(len(inLines2)):
        if inLines2[q][:2]!="# ":
            inLines2[q]=inLines2[q].replace(defines1[t],defines2[t])

for t in range(len(vars1)):
    if verb:
        print("Replace vars, '"+vars1[t]+"' to '"+vars2[t]+"'.")
    for q in range(len(inLines2)):
        if inLines2[q][:2]!="# ":
            inLines2[q]=wordsReplace(inLines2[q],vars1[t],vars2[t])

if not skipCm:
    inLines=[]
    for x in range(len(inLines2)):
        if len(inLines2[x].strip())>0:
            if inLines2[x].lstrip()[:2]=="# ":
                if verb:
                    print("Add a comment to line " + str(x))
                inLines.append("REM " + inLines2[x].strip()[2:])
            else:
                inLines.append(inLines2[x])
        else:
            if verb:
                print("Skip empty line on row " + str(x))
else:
    inLines=[]
    for x in range(len(inLines2)):
        if len(inLines2[x].strip())>0:
            if inLines2[x].lstrip()[:2]!="# ":
                inLines.append(inLines2[x])
            else:
                if verb:
                    print("Skip the comment on line " + str(x))            
        else:
            if verb:
                print("Skip empty line on row " + str(x))

skipAddress=100000
for x in range(len(inLines)):
    if inLines[x].lstrip()[:5]=="WHEN ":
        y=x+1
        skipLabel=None
        while skipLabel==None and y<len(inLines):
            if inLines[y].lstrip()[:4]=="SKIP":
                skipLabel="@SKIP"+str(skipAddress)+":"
                inLines[y]=skipLabel
                if y==len(inLines)-1:
                    inLines.append(":")
                skipAddress=skipAddress+1
            y=y+1
        inLines[x]=inLines[x].replace("WHEN ","IFNOT(")
        inLines[x]=inLines[x].rstrip()+") THEN GOTO "+skipLabel

m=0
for t in inLines:
    if len(t)>0 and t[0]!="@":
        m=m+1
outLines=[None]*m
x=0
m=0
seq=seqStep
labelNames=[]
labelSeqs=[]
for t in inLines:
    if len(t)>0 and t[0]!="@":
        if verb:
            print("Add sequence '"+str(seq)+"' to line " + str(x))
        outLines[m]=str(seq)+" "+t.strip()
        seq=seq+seqStep
        m=m+1
    elif len(t)>0 and t[0]=="@":
        if verb:
            print("Set the sequence '"+str(seq)+"' to label " + t.strip())
        labelNames.append(t.strip())
        labelSeqs.append(seq)
    x=x+1
for t in range(len(outLines)):
    if "GOTO" in outLines[t] or "GOSUB" in outLines[t]:
        tmp=outLines[t]
        for q in range(len(labelNames)):
            if verb:
                print("Replace the label '" + labelNames[q] + "' to sequence '" + str(labelSeqs[q]) + "' on line " + str(t))
            outLines[t]=outLines[t].replace(labelNames[q],str(labelSeqs[q]))
        if tmp==outLines[t]:
            print("Error: Could not found the label in command '"+tmp.split()[1]+" "+tmp.split()[2]+"'")
            errs=True
if not errs:
    with open(outFile, 'w') as f:
        f.writelines('\n'.join(outLines))
    print("Output file has been created successfully.")
else:
    print("There are errors!")
