import sys
sys.path.append('/home/verbs/student/adwi9965/Thyme/github')
sys.path.append('/home/verbs/shared/anafora4python')

import argparse
from iaa.util import *
from iaa.reference_coreference_scorers import averaged_scorer
from iaa.anafora2conll import make_conll_file

def is_good_qualtiative_example(iaa_score, ann1_total, ann2_total):
  """
  Criteria for determining if the 2 docs should be looked at
   for good examples of agreements/disagreements
  """
  return iaa_score > .3 and iaa_score < 1 and ann1_total > 3 and ann2_total > 3

if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Check con-sub iaa and print some positive and negative examples")
  parser.add_argument('--doc1', help="doc1 path", required=True)
  parser.add_argument('--doc2', help="doc2 path", required=True)

  args = parser.parse_args()
  doc1path = args.doc1
  doc2path = args.doc2
  doc1fn = doc1path.split('/')[-1]
  doc2fn = doc2path.split('/')[-1]
  doc1 = get_annotation_document(doc1path, doc1fn)
  doc2 = get_annotation_document(doc2path, doc2fn)

  mode = "loose"
  setting="cross-doc"

  # Will return (None, None) if no CON-SUB annotations.
  make_conll_file(doc1path, './coref-conll-files/%s/%s' % (mode, doc1fn), mode=mode, setting=setting)
  make_conll_file(doc2path, './coref-conll-files/%s/%s' % (mode, doc2fn), mode=mode, setting=setting)

  # Run reference scorer
  score = averaged_scorer.get_averaged_score('./coref-conll-files/%s/%s' % (mode, doc1fn), \
                                             './coref-conll-files/%s/%s' % (mode, doc2fn))
  print(score)


