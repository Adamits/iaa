from calculations import get_crossdoc_agreement_by_structural_reltypes
import sys
sys.path.append('/Users/ajwieme/verbs-projects/thyme/iaa')
from util import get_annotation_document

if __name__ == "__main__":
  dir = "/Users/ajwieme/verbs-projects/thyme/anaforaProjectFile/Cross-THYMEColonFinal/Train/ID097"
  doc1fn = "ID097.Thyme2v1-Correction.jadu7853.completed.xml"
  doc1path = dir + '/' + doc1fn
  doc2fn = "ID097.Thyme2v1-Correction.reganma.completed.xml"
  doc2path = dir + '/' + doc2fn

  doc1 = get_annotation_document(doc1path, doc1fn)
  doc2 = get_annotation_document(doc2path, doc2fn)

  # Will return (None, None) if no CON-SUB annotations.
  print(get_crossdoc_agreement_by_structural_reltypes(doc1, doc2, ["contains-subevent", "whole-part", "set-subset"]))

