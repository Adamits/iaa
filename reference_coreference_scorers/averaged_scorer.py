from subprocess import check_output
import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def get_f1(s):
  accs = s.split('\n')[-3]
  f1string = accs.split('\t')[-1]
  f1 = float(f1string.split()[-1][:-1])
  return f1

def get_averaged_score(key, ref):
  blanc = check_output(["perl", CURRENT_PATH + "/scorer.pl", "blanc", key, ref]).decode("utf-8")
  muc = check_output(["perl", CURRENT_PATH + "/scorer.pl", "muc", key, ref]).decode("utf-8")
  bcub = check_output(["perl", CURRENT_PATH + "/scorer.pl", "bcub", key, ref]).decode("utf-8")
  ceafe = check_output(["perl", CURRENT_PATH + "/scorer.pl", "ceafe", key, ref]).decode("utf-8")

  return round(sum([get_f1(blanc), get_f1(muc), get_f1(bcub), get_f1(ceafe)]) / 4, 2)

if __name__=='__main__':
  key = CURRENT_PATH + "/test/DataFiles/TC-L.key"
  ref = CURRENT_PATH + "/test/DataFiles/TC-L-1.response"
  print(get_averaged_score(key, ref))
