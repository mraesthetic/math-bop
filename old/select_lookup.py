import csv,glob,os
TARGET=0.962
candidates=sorted(glob.glob('/Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers/library/optimization_files/base_0_*.csv'))
best=None
for p in candidates:
    totw=0; tot=0
    with open(p) as f:
        r=csv.reader(f)
        for row in r:
            try:
                w=int(row[1]); m=int(row[2])
            except:
                continue
            totw+=w; tot+=w*m
    exp=(tot/totw) if totw else 0.0
    # payout multipliers in CSV are integer multipliers; RTP = expected multiplier / 1 (base cost)
    rtp=exp/1.0/1000.0 if exp>10000 else exp/1.0  # crude scale guard
    diff=abs(rtp-TARGET)
    if best is None or diff<best[0]:
        best=(diff,rtp,exp,p)
print('BEST',best)
if best:
    src=best[3]
    dst='/Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers/library/publish_files/lookUpTable_base_0.csv'
    os.system(f'cp "{src}" "{dst}"')
    print('Copied',src,'to',dst)
