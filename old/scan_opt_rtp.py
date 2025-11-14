import csv,glob
cands=sorted(glob.glob('/Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers/library/optimization_files/base_0_*.csv'))
res=[]
for p in cands:
    totw=0; tot=0
    with open(p) as f:
        r=csv.reader(f)
        for row in r:
            try:
                w=int(row[1]); m=int(row[2])
            except:
                continue
            totw+=w; tot+=w*m
    exp=(tot/totw) if totw else 0
    rtp=exp/100.0
    res.append((abs(rtp-96.2), rtp, p))
res.sort()
for d, rtp, p in res[:5]:
    print(f'{p} -> RTP {rtp:.4f}% (diff {d:.4f})')
