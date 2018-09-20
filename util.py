from anafora4python import annotation
from bs4 import BeautifulSoup as soup
import glob

def get_annotation_document(xml_path, FN):
  try:
    doc = annotation.Document(soup(open(xml_path), "xml"), FN)
    return doc
  except Exception as e:
    print("Error for %s: %s" % (FN, e))
    return None

def get_annotation_text_document(xml_path, FN):
  try:
    doc = annotation.Document(soup(open(xml_path), "xml"), FN)
    return doc
  except Exception as e:
    print("Error for %s: %s" % (FN, e))
    return None

def get_annotator(fn):
  """
  Get 3rd slot in the filename,
  which should have the annotator name
  """
  return fn.split('.')[2]

def has_annotator(fn):
  """
  Search annotator name and if it is not in the
  list of auto generated info, assume it is
  an actual annotator.

  Return: Bool
  """
  NOT_ANNOTATOR = ["gold", "auto", "preannotation"]
  return get_annotator(fn) not in NOT_ANNOTATOR

def get_other_annotator_filename(root, fn):
  wildcard_fn = fn.split(".")
  author = wildcard_fn[2]
  # replace annotator name with kleene star
  wildcard_fn[2] = "*"

  # Get the path of all annotations for that document
  all_anns = glob.glob(root + '/' + '.'.join(wildcard_fn))
  # Get jsut the filenames
  all_anns = [a.split("/")[-1] for a in all_anns]
  # Only return those that have an actual annotator (e.g. no 'gold', 'Adjudication', etc)
  # That is, s
  all_anns = [a for a in all_anns if has_annotator(a)]

  if len(all_anns) > 2:
    raise Exception("more than two annotators! %s" % ', '.join(all_anns))
  elif len(all_anns) == 2:
    # Get the document that doesn't have author name in it.
    return [a for a in all_anns if get_annotator(a) != author][0]
  else:
    return None

