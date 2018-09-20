import os
import codecs
from bs4 import BeautifulSoup as soup
from reference_coreference_scorers import averaged_scorer
from anafora2conll import make_conll_file
from anafora4python import annotation

import statistics

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


def get_note_filename(note_name, schema_name, annotator, status):
  """
  Use info on the note to formulate the actual filename.
  This can be used to get a Document object.
  """
  name = note_name.split('/')[-1]
  return name + '.' + schema_name + '.' + annotator + '.' + status + '.xml'

def get_iaa_scores(data_dir, mode="loose", setting="single-doc"):
  crossdoc_pass = CrossDocPass('Thyme2v1-Correction', data_dir + '/Cross-THYMEColonFinal/')
  # For overall IAA
  scores = []
  for note_name in crossdoc_pass.notes:
    # Second pass:
    annotators = list(crossdoc_pass.notes[note_name].keys())
    if len(annotators) > 1:
      annotators_dict = crossdoc_pass.notes[note_name]
      directory = crossdoc_pass.directory
      schema_name = crossdoc_pass.schema_name
      # Generate conll files
      annotators = list(annotators_dict.keys())
      statuses = list(annotators_dict.values())
      doc1fn = get_note_filename(note_name, schema_name, annotators[0], statuses[0])
      doc1path = directory + note_name + '/' + doc1fn
      doc2fn = get_note_filename(note_name, schema_name, annotators[1], statuses[1])
      doc2path = directory + note_name + '/' + doc2fn
      make_conll_file(doc1path, './coref-conll-files/%s/%s' % (mode, doc1fn), mode=mode, setting=setting)
      make_conll_file(doc2path, './coref-conll-files/%s/%s' % (mode, doc2fn), mode=mode, setting=setting)

      # Run reference scorer
      score = averaged_scorer.get_averaged_score('./coref-conll-files/%s/%s' % (mode, doc1fn),\
                                                './coref-conll-files/%s/%s' % (mode, doc2fn))
      print("%s: %s - %s: %.2f" % (mode, doc1fn, doc2fn, score))
      scores.append(score)

  return scores

if __name__=='__main__':
  #loose_scores = get_iaa_scores("/Users/ajwieme/verbs-projects/thyme/anaforaProjectFile/", setting="cross-doc")
  loose_scores = get_iaa_scores("/data/anafora/anaforaProjectFile/", setting="cross-doc")
  #strict_scores = get_iaa_scores("/Users/ajwieme/verbs-projects/thyme/anaforaProjectFile/", mode="strict", setting="cross-doc")
  strict_scores = get_iaa_scores("/data/anafora/anaforaProjectFile/", mode="strict", setting="cross-doc")
  #extra_strict_scores = get_iaa_scores("/Users/ajwieme/verbs-projects/thyme/anaforaProjectFile/", mode="extra_strict",
  #                               setting="cross-doc")
  extra_strict_scores = get_iaa_scores("/data/anafora/anaforaProjectFile/", mode="extra_strict", setting="cross-doc")
  print("Loose Cross-Doc Coref Average Score: %.2f%% over %i documents"
        % (sum(loose_scores) / float(len(loose_scores)), len(loose_scores)))
  print("Standard Deviation: %.2f" % statistics.stdev(loose_scores))
  print("Strict Cross-Doc Coref Average Score: %.2f%% over %i documents"
        % (sum(strict_scores) / float(len(strict_scores)), len(strict_scores)))
  print("Standard Deviation: %.2f" % statistics.stdev(strict_scores))
  print("Extra Strict Cross-Doc Coref Average Score: %.2f%% over %i documents"
        % (sum(strict_scores) / float(len(extra_strict_scores)), len(extra_strict_scores)))
  print("Standard Deviation: %.2f" % statistics.stdev(extra_strict_scores))
