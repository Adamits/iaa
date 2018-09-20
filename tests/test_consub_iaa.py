import sys
sys.path.append('/home/verbs/student/adwi9965/Thyme/github')
sys.path.append('/home/verbs/shared/anafora4python')

import argparse
from iaa.relations.calculations import get_relation_agreement_by_type
from iaa.relations.crossdoc.calculations import get_crossdoc_agreement_by_structural_reltypes
from iaa.util import *

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

  doc1 = get_annotation_document(doc1path, doc1path.split('/')[-1])
  doc2 = get_annotation_document(doc2path, doc2path.split('/')[-1])

  # Will return (None, None) if no CON-SUB annotations.
  reltypes = ["contains-subevent"]
  iaa_dict_l = get_crossdoc_agreement_by_structural_reltypes(doc1, doc2, mode='loose', reltypes=reltypes)
  print(iaa_dict_l['contains-subevent'])
  iaa_dict_s = get_crossdoc_agreement_by_structural_reltypes(doc1, doc2, mode='strict', reltypes=reltypes)
  print(iaa_dict_s['contains-subevent'])


