"""
Cross-doc contains-subevent agreement

By Adam Wiemerslage: 6/25/2018
"""

import argparse
import os

from relations.calculations import get_relation_agreement_by_type
from util import *

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Contains-subevent single-doc inter annotator agreement")
  parser.add_argument('--input', help="Input folder", required=True)
  parser.add_argument('--file_type', default="none", help="Enter file identifier ( Thyme2v1-Correction.)")

  args = parser.parse_args()
  input_folder = parser.parse_args().input
  file_type = parser.parse_args().file_type
  calculated = []

  for root, directories, filenames in os.walk(input_folder):
    if "clinic" in root.split("/")[-1] or "path" in root.split("/")[-1]:
      # SINGLE DOC
      continue
    else:
      # CROSS DOC
      if filenames and any(".xml" in filename for filename in filenames):
        for filename in filenames:
          if file_type != "none":
            if file_type not in filename:
              continue
          if filename.endswith(".xml"):
            if has_annotator(filename) and filename not in calculated:
              filename2 = get_other_annotator_filename(root, filename)
              calculated.append(filename)
              if filename2:
                calculated.append(filename2)
                print(filename, filename2)

                doc1 = get_annotation_document(root + "/" + filename, filename)
                doc2 = get_annotation_document(root + "/" + filename2, filename2)

                percent, total_doc1, total_doc2 = get_relation_agreement_by_type(doc1, doc2, 'contains-subevent', setting="cross-doc")
                if percent:
                  print(percent, total_doc1 + total_doc2)
                else:
                  print("Nothing to show for this one...")