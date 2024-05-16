python.exe btrend.py "-in=charshapes.basic.txt" "-out=charshapes.basic.out.txt" -step=5 -s -t
c64list charshapes.basic.out.txt -ovr -prg:hu-chars.prg
rem del charshapes.basic.out.txt
