import os
import datetime
import sys

#sys.path.append('/User/ajwieme/verbs-projects/thyme')
sys.path.append('/home/verbs/student/adwi9965/Thyme')
sys.path.append('/home/verbs/shared/anafora4python')
from iaa.relations.calculations import get_relation_agreement_by_type
from iaa.relations.crossdoc.calculations import get_crossdoc_agreement_by_structural_reltypes
from iaa.util import *

import statistics

#DATA_DIR = '/data/anafora/anaforaProjectFile/'
DATA_DIR = '/Users/ajwieme/verbs-projects/thyme/anaforaProjectFile'

class Pass:
  def __init__(self, schema_name, directory):
    self.notes = dict()
    self.directory = directory
    self.schema_name = schema_name
    for root, subFolders, files in os.walk(directory):
      for file in files:
        if '.' + schema_name + '.' in file and 'preannotation' in file:
          split = file.split('.')
          note_name = root.split('/')[-2] + '/' + split[-5]
          if note_name not in self.notes:
            self.notes[note_name] = dict()
        if '.' + schema_name + '.' in file and 'preannotation' not in file and 'gold' not in file:
          split = file.split('.')
          note_name = root.split('/')[-2] + '/' + split[-5]
          annotator = split[-3]
          status = split[-2]
          if note_name not in self.notes:
            self.notes[note_name] = dict()
          self.notes[note_name][annotator] = status


class CrossDocPass:
  def __init__(self, schema_name, directory):
    self.notes = dict()
    self.directory = directory
    self.schema_name = schema_name
    for root, subFolders, files in os.walk(directory):
      for file in files:
        if '.' + schema_name + '.' in file and 'preannotation' in file:
          note_name = root.split('/')[-3] + '/' + os.path.join(root, file).split('/')[-3]
          if note_name not in self.notes:
            self.notes[note_name] = dict()
        if '.' + schema_name + '.' in file and 'preannotation' not in file and 'gold' not in file:
          split = file.split('.')
          note_name = root.split('/')[-2] + '/' + split[-5]
          annotator = split[-3]
          status = split[-2]
          if note_name not in self.notes:
            self.notes[note_name] = dict()
          self.notes[note_name][annotator] = status

def is_good_qualtiative_example(iaa_score, ann1_total, ann2_total):
  """
  Criteria for determining if the 2 docs should be looked at
   for good examples of agreements/disagreements
  """
  return False#iaa_score > .2 and iaa_score < 1 and ann1_total > 0 and ann2_total > 0

def print_stats(scores, rels_count):
  print("\t%.2f%% for % i relations in %i documents" \
    % ((sum(scores) / len(scores)), rels_count, len(scores)))
  print("\t Highest Score: %.2f" % max(scores))
  print("\t Lowest Score: %.2f" % min(scores))
  print("\t Standard Deviation: %.2f\n" % statistics.stdev(scores))

def get_note_filename(note_name, schema_name, annotator, status):
  """
  Use info on the note to formulate the actual filename.
  This can be used to get a Document object.
  """
  name = note_name.split('/')[-1]
  return name + '.' + schema_name + '.' + annotator + '.' + status + '.xml'

def strip_leading_underscore_from_fn(note_name):
  """
  Some notenames seem to have a leading '_' that isn't in the directory name

   Need to split on the directory '/', and then remove potential leading '-' from the
   filename portion of the path
  """
  path_list = note_name.split('/')
  path_list[1] = path_list[1].lstrip('_')
  return '/'.join(path_list)

def get_iaa_score(directory, note_name, schema_name, annotators_dict, mode="loose", type="contains-subevent"):
  """
  Given the note info, calculate an IAA score. This is for Single Doc only

  annotators_dict is the note_dict[note_name], with
  {annotator_name: status, ...}
  """
  annotators = list(annotators_dict.keys())
  statuses = list(annotators_dict.values())
  doc1fn = get_note_filename(note_name, schema_name, annotators[0], statuses[0])
  doc1path = directory + strip_leading_underscore_from_fn(note_name) + '/' + doc1fn
  doc2fn = get_note_filename(note_name, schema_name, annotators[1], statuses[1])
  doc2path = directory + strip_leading_underscore_from_fn(note_name) + '/' + doc2fn

  doc1 = get_annotation_document(doc1path, doc1fn)
  doc2 = get_annotation_document(doc2path, doc2fn)

  # Will return (None, None) if no CON-SUB annotations.
  percentage, total_ann1, total_ann2 = get_relation_agreement_by_type(doc1, doc2, type, mode=mode, setting="single-doc")

  if percentage is not None and is_good_qualtiative_example(percentage, total_ann1, total_ann2):
    print("%s vs %s" % (doc1path, doc2path))
    print("Score: %.2f" % percentage)
    print("Totals: %i and %i" % (total_ann1, total_ann2))

  if percentage is not None:
    return (round(percentage * 100, 2), total_ann1, total_ann2)
  else:
    return (None, None, None)

def get_crossdoc_iaa_score(directory, note_name, schema_name, annotators_dict, mode="loose", types=["contains-subevent"]):
  """
    Given the note info, calculate an IAA score. for crossdoc for all annotation types in types.

    annotators_dict is the note_dict[note_name], with
    {annotator_name: status, ...}
    """

  annotators = list(annotators_dict.keys())
  statuses = list(annotators_dict.values())
  doc1fn = get_note_filename(note_name, schema_name, annotators[0], statuses[0])
  doc1path = directory + strip_leading_underscore_from_fn(note_name) + '/' + doc1fn
  doc2fn = get_note_filename(note_name, schema_name, annotators[1], statuses[1])
  doc2path = directory + strip_leading_underscore_from_fn(note_name) + '/' + doc2fn

  doc1 = get_annotation_document(doc1path, doc1fn)
  doc2 = get_annotation_document(doc2path, doc2fn)

  # Will return (None, None) if no CON-SUB annotations.
  reltypes = ["contains-subevent", "whole-part", "set-subset"]
  iaa_dict = get_crossdoc_agreement_by_structural_reltypes(doc1, doc2, mode=mode, reltypes=reltypes)

  for reltype, v in iaa_dict.items():
    score, total_ann1, total_ann2 = v
    if score is not None and is_good_qualtiative_example(score, total_ann1, total_ann2):
      print("%s vs %s" % (doc1path, doc2path))
      print("Score: %.2f" % score)
      print("Totals: %i and %i" % (total_ann1, total_ann2))

  return iaa_dict

def get_iaa_scores(data_dir):
  coref_first_pass = Pass('Temporal-THYME2ReGold', DATA_DIR + '/THYMEColonFinal/')
  coref_second_pass = Pass('Thyme2v1-Coreference', data_dir + '/THYMEColonFinal/')
  crossdoc_pass = CrossDocPass('Thyme2v1-Correction', data_dir + '/Cross-THYMEColonFinal/')

  within_doc = False

  if within_doc:
    # For overall IAA
    scores = []
    rels_count = 0
    for note_name in coref_first_pass.notes:
      if note_name in coref_second_pass.notes:
        annotators = list(coref_second_pass.notes[note_name].keys())
        if len(annotators) > 1:
          iaa_score, ann1_total, ann2_total = get_iaa_score(coref_second_pass.directory,
                                                            note_name,
                                                            coref_second_pass.schema_name,
                                                            coref_second_pass.notes[note_name]
                                                            )
          if iaa_score is not None:
            scores.append(iaa_score)
            rels_count += ann1_total + ann2_total

    print("WITHIN DOC LOOSE SCORES CON SUB:")
    print_stats(scores, rels_count)

  # For overall IAA
  total_crossdoc_rels = {}
  all_scores = {}
  for note_name in crossdoc_pass.notes:
    annotators = list(crossdoc_pass.notes[note_name].keys())
    if len(annotators) > 1:
      crossdoc_iaa_dict = get_crossdoc_iaa_score(crossdoc_pass.directory,
                                                 note_name, crossdoc_pass.schema_name,
                                                 crossdoc_pass.notes[note_name])
      for reltype, v in crossdoc_iaa_dict.items():
        score, ann1_count, ann2_count = v
        if score is not None:
          total_crossdoc_rels.setdefault(reltype, 0)
          score = round(score * 100, 2)
          total_crossdoc_rels[reltype] += ann1_count + ann2_count
          all_scores.setdefault(reltype, [])
          all_scores[reltype] += [score]

  print("CrossDoc Loose scores:")
  for relation_type, scores in all_scores.items():
    if relation_type == "whole-part":
      print("CROSS-DOC WHOLE-PART:")
    elif relation_type == "set-subset":
      print("CROSS-DOC SET-SUBSET:")
    elif relation_type == "contains-subevent":
      print("CROSS-DOC CON-SUB:")

    print_stats(scores, total_crossdoc_rels[relation_type])

  if within_doc:
    scores = []
    total_rels_count = 0
    for note_name in coref_second_pass.notes:
      annotators = list(coref_second_pass.notes[note_name].keys())
      if len(annotators) > 1:
        iaa_score, ann1_total, ann2_total = get_iaa_score(coref_second_pass.directory,
                                                          note_name,
                                                          coref_second_pass.schema_name,
                                                          coref_second_pass.notes[note_name],
                                                          mode="strict")
        if iaa_score is not None:
          scores.append(iaa_score)
          total_rels_count += ann1_total + ann2_total

    print("WITHIN DOC STRICT CON-SUB:")
    print_stats(scores, total_rels_count)

  total_crossdoc_rels = {}
  all_scores = {}
  for note_name in crossdoc_pass.notes:
    annotators = list(crossdoc_pass.notes[note_name].keys())
    if len(annotators) > 1:
      crossdoc_iaa_dict = get_crossdoc_iaa_score(crossdoc_pass.directory,
                                                 note_name, crossdoc_pass.schema_name,
                                                 crossdoc_pass.notes[note_name],
                                                 mode="strict")
      for reltype, v in crossdoc_iaa_dict.items():
        score, ann1_count, ann2_count = v
        if score is not None:
          total_crossdoc_rels.setdefault(reltype, 0)
          score = round(score * 100, 2)
          total_crossdoc_rels[reltype] += ann1_count + ann2_count
          all_scores.setdefault(reltype, [])
          all_scores[reltype] += [score]

  print("CrossDoc Strict Scores:")
  for relation_type, scores in all_scores.items():
    if relation_type == "whole-part":
      print("CROSS-DOC WHOLE-PART:")
    elif relation_type == "set-subset":
      print("CROSS-DOC SET-SUBSET:")
    elif relation_type == "contains-subevent":
      print("CROSS-DOC CON-SUB:")

    print_stats(scores, total_crossdoc_rels[relation_type])


if __name__=='__main__':
  get_iaa_scores(DATA_DIR)
