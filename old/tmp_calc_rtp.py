import csv
base_csv = '/Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers/library/publish_files/lookUpTable_base_0.csv'
bonus_csv = '/Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers/library/publish_files/lookUpTable_bonus_0.csv'

def calc(path, denom):
    totw=0
    tot=0
    with open(path) as f:
        r=csv.reader(f)
        for row in r:
            try:
                w=int(row[1]); p=int(row[2])
            except:
                continue
            totw+=w; tot+=w*p
    exp = (tot/totw) if totw else 0
    return exp/denom

print('BASE_RTP', calc(base_csv, 1))
print('BONUS_BUY_RTP', calc(bonus_csv, 100))
