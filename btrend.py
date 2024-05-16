import sys
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
defines1=[]
defines2=[]
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
        if not testCase:
            inLines2[t]="\t"+inLines2[t].strip()[2:]
        else:
            inLines2[t]=""
    elif inLines2[t].strip()[:2]=="? ":
        if not testCase:
            inLines2[t]=""
        else:
            inLines2[t]="\t"+inLines2[t].strip()[2:]
    t=t+1

for t in range(len(inLines2)):
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
        defines1.append(varName)
        defines2.append(varRealName)
        varIndex2 = varIndex2 + 1
        if varIndex2==len(var2nd):
            varIndex1 = varIndex1 + 1
            varIndex2 = 0
        inLines2[t]=""
for t in range(len(defines1)):
    if verb:
        print("Replace defines, '"+defines1[t]+"' to '"+defines2[t]+"'.")
    for q in range(len(inLines2)):
        if inLines2[q][:2]!="# ":
            inLines2[q]=inLines2[q].replace(defines1[t],defines2[t])
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
